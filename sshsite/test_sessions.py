import argparse
import asyncio
import os
import time
import asyncssh

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3333

async def _open_session(host, port, username, hold_seconds, idx):
    conn = None
    chan = None
    try:
        conn = await asyncssh.connect(
            host,
            port=port,
            username=username,
            known_hosts=None,
        )
        result = await conn.create_session(asyncssh.SSHClientSession, term_type="xterm")
        if isinstance(result, tuple) and len(result) == 2:
            session, chan = result
        else:
            chan = result
        await asyncio.sleep(hold_seconds)
        return True
    except Exception:
        return False
    finally:
        if chan is not None:
            try:
                chan.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
                await conn.wait_closed()
            except Exception:
                pass

async def run(count, hold_seconds, host, port, username):
    tasks = [
        asyncio.create_task(_open_session(host, port, username, hold_seconds, idx))
        for idx in range(count)
    ]
    results = await asyncio.gather(*tasks)
    accepted = sum(1 for r in results if r)
    rejected = count - accepted
    return accepted, rejected


def main():
    parser = argparse.ArgumentParser(description="Open many SSH sessions to test the cap.")
    parser.add_argument("--count", type=int, default=25)
    parser.add_argument("--hold", type=float, default=10.0)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--username", default=os.environ.get("USER") or "unknown")
    args = parser.parse_args()

    start = time.time()
    accepted, rejected = asyncio.run(
        run(args.count, args.hold, args.host, args.port, args.username)
    )
    elapsed = time.time() - start

    print("Requested sessions:", args.count)
    print("Accepted sessions:", accepted)
    print("Rejected sessions:", rejected)
    print("Elapsed seconds:", round(elapsed, 2))


if __name__ == "__main__":
    main()
