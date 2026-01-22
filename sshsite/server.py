import asyncio, asyncssh
import os, subprocess, sys, pty, fcntl, termios, struct
import threading
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE = Path(__file__).resolve().parent
APP = BASE / "app.py"

LOG_PATH = BASE / "logs/server.log"

HOST = os.environ.get("SSH_HOST", "127.0.0.1")
PORT = int(os.environ.get("SSH_PORT", "3333"))
HOST_KEY_PATH = Path(os.environ.get("SSH_HOST_KEY", str(BASE / "dev_host_key")))

_handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3)
_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
_handler.setFormatter(_formatter)
logging.basicConfig(level=logging.INFO, handlers=[_handler])

# limit max concurrent sessions to 20
MAX_SESSIONS = 20
_active_sessions = 0
_active_sessions_lock = threading.Lock()

def _get_active_sessions():
    with _active_sessions_lock:
        return _active_sessions

def _try_reserve_session():
    global _active_sessions
    with _active_sessions_lock:
        if _active_sessions >= MAX_SESSIONS:
            return False
        _active_sessions += 1
        return True

def _release_session():
    global _active_sessions
    with _active_sessions_lock:
        if _active_sessions > 0:
            _active_sessions -= 1

class Server(asyncssh.SSHServer):
    def __init__(self):
        self._peer = None
        self._username = None

    def begin_auth(self, username):
        self._username = username
        logging.info(
            "auth accepted user=%s client=%s reason=%s",
            username,
            self._peer,
            "no_auth_required",
        )
        return False  # no auth for now (dev)
    
    def connection_made(self, conn):
        self._peer = conn.get_extra_info("peername")
        logging.info("connection accepted user=%s client=%s", self._username, self._peer)
        return super().connection_made(conn)

    def connection_lost(self, exc):
        if exc:
            logging.info(
                "connection rejected/ended user=%s client=%s reason=%s",
                self._username,
                self._peer,
                exc,
            )
        else:
            logging.info(
                "connection ended user=%s client=%s",
                self._username,
                self._peer,
            )
        return super().connection_lost(exc)
    
    def session_requested(self):
        if not _try_reserve_session():
            logging.info(
                "session rejected user=%s client=%s reason=%s active=%s max=%s",
                self._username,
                self._peer,
                "max_sessions_reached",
                _get_active_sessions(),
                MAX_SESSIONS,
            )
            return False
        logging.info(
            "session accepted user=%s client=%s active=%s max=%s",
            self._username,
            self._peer,
            _get_active_sessions(),
            MAX_SESSIONS,
        )
        return AppSession(_release_session)


def _set_pty_size(fd, rows, cols, pix_w=0, pix_h=0):
    if rows is None or cols is None:
        return
    size = struct.pack("HHHH", rows, cols, pix_w or 0, pix_h or 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, size)


class AppSession(asyncssh.SSHServerSession):
    def __init__(self, on_close):
        self._chan = None
        self._pty_manager = None
        self._pty_subsidiary = None
        self._proc = None
        self._reader_task = None
        self._wait_task = None
        self._term_type = None
        self._term_size = None
        self._on_close = on_close
        self._released = False

    def connection_made(self, chan):
        self._chan = chan
        self._chan.set_encoding(None)  # raw bytes for TUI
        peer = self._chan.get_extra_info("peername")
        user = self._chan.get_extra_info("username")
        logging.info("session start user=%s client=%s", user, peer)

    def pty_requested(self, term_type, term_size, term_modes):
        self._term_type = term_type
        self._term_size = term_size
        return True

    def terminal_size_changed(self, width, height, pixwidth, pixheight):
        if self._pty_manager is not None:
            _set_pty_size(self._pty_manager, height, width, pixwidth, pixheight)

    def shell_requested(self):
        self._pty_manager, self._pty_subsidiary = pty.openpty()
        if self._term_size:
            cols, rows, pix_w, pix_h = self._term_size
            _set_pty_size(self._pty_subsidiary, rows, cols, pix_w, pix_h)
        env = os.environ.copy()
        if self._term_type:
            env["TERM"] = self._term_type

        self._proc = subprocess.Popen(
            [sys.executable, str(APP)],
            stdin=self._pty_subsidiary,
            stdout=self._pty_subsidiary,
            stderr=self._pty_subsidiary,
            env=env,
            close_fds=True,
        )
        os.close(self._pty_subsidiary)
        self._pty_subsidiary = None

        loop = asyncio.get_running_loop()
        self._reader_task = loop.create_task(self._forward_pty_to_ssh())
        self._wait_task = loop.create_task(self._wait_for_proc())
        return True

    async def _forward_pty_to_ssh(self):
        try:
            while True:
                data = await asyncio.to_thread(os.read, self._pty_manager, 1024)
                if not data:
                    break
                self._chan.write(data)
        except Exception:
            pass
        finally:
            if self._chan:
                self._chan.exit(0)

    async def _wait_for_proc(self):
        if not self._proc:
            return
        await asyncio.to_thread(self._proc.wait)
        if self._pty_manager is not None:
            try:
                os.close(self._pty_manager)
            except OSError:
                pass
            self._pty_manager = None
        if self._chan:
            self._chan.exit(self._proc.returncode or 0)

    def data_received(self, data, datatype):
        if self._pty_manager is not None:
            os.write(self._pty_manager, data)

    def eof_received(self):
        if self._pty_manager is not None:
            try:
                os.close(self._pty_manager)
            except OSError:
                pass
            self._pty_manager = None
        return False

    def connection_lost(self, exc):
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
        if self._pty_manager is not None:
            try:
                os.close(self._pty_manager)
            except OSError:
                pass
            self._pty_manager = None
            
        # extra info collection for logging
        peer = self._chan.get_extra_info("peername") if self._chan else None
        user = self._chan.get_extra_info("username") if self._chan else None
        if exc:
            logging.info("session end user=%s client=%s reason=%s", user, peer, exc)
        else:
            logging.info("session end user=%s client=%s", user, peer)
        if not self._released:
            self._released = True
            self._on_close()
            logging.info("session count active=%s max=%s", _get_active_sessions(), MAX_SESSIONS)

async def main():
    # Generate a temp host key if not present
    key_path = HOST_KEY_PATH
    if not key_path.exists():
        key = asyncssh.generate_private_key("ssh-ed25519")
        key_path.write_text(key.export_private_key("openssh").decode())
    try:
        os.chmod(key_path, 0o600)
    except OSError:
        logging.warning("unable to set permissions on host key path=%s", key_path)

    await asyncssh.create_server(
        Server,
        host=HOST,
        port=PORT,
        server_host_keys=[str(key_path)],
        allow_scp=False,
    )
    
    if HOST in {"127.0.0.1", "::1", "localhost"}:
        logging.warning(
            "host is loopback; set SSH_HOST=0.0.0.0 to accept public connections"
        )
    print(f"Listening on ssh://{HOST}:{PORT}")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
