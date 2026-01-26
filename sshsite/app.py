from random import choice, randint, random
import time
from typing import Iterable

from rich.text import Text
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.theme import Theme

from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

HOME = r"""Welcome to aidanek.dev

Press ? for help

       .__    .___                     __            .___           
_____  |__| __| _/____    ____   ____ |  | __      __| _/_______  __
\__  \ |  |/ __ |\__  \  /    \_/ __ \|  |/ /     / __ |/ __ \  \/ /
 / __ \|  / /_/ | / __ \|   |  \  ___/|    <     / /_/ \  ___/\   / 
(____  /__\____ |(____  /___|  /\___  >__|_ \ /\ \____ |\___  >\_/  
     \/        \/     \/     \/     \/     \/ \/      \/    \/     
     
     
"""

HELP = """Help / Controls

h · home
? · help
r · resume
^p · search
q · quit
"""

RESUME = """Aidan Elliott-Korytek

Security · Systems · Networking

Skills

Python, Java, C, Linux, Server Hardening, Binary Exploitation

Projects

- aidanek.dev interactive portfolio (asyncssh, Textual)

- SSH config command line utility

Full resume (PDF): https://aidanek.dev/resume.pdf
"""

SPLASH = r"""
====================================================================
       .__    .___                     __            .___           
_____  |__| __| _/____    ____   ____ |  | __      __| _/_______  __
\__  \ |  |/ __ |\__  \  /    \_/ __ \|  |/ /     / __ |/ __ \  \/ /
 / __ \|  / /_/ | / __ \|   |  \  ___/|    <     / /_/ \  ___/\   / 
(____  /__\____ |(____  /___|  /\___  >__|_ \ /\ \____ |\___  >\_/  
     \/        \/     \/     \/     \/     \/ \/      \/    \/      
====================================================================
"""

THEME = Theme(
    name="aidanek",
    primary="#ff8a00",
    secondary="#ffb347",
    accent="#ff6a00",
    foreground="#ffd7a6",
    background="#0b0b0b",
    surface="#111111",
    panel="#1a1a1a",
    boost="#ff8a0040",
    success="#ff8a00",
    warning="#ffb347",
    error="#ff6a00",
    dark=True,
)

ACCENT_COLOR = "#ff6a00"

class RainSplash(Static):
    RAIN_COLORS = [
        "#ff6a00",
        "#ff8a00",
        "#ffb347",
        "#ffd7a6",
        "#0b0b0b",
    ]

    def on_mount(self) -> None:
        self._drops = []
        self._last_size = (0, 0)
        self._pulsing = True
        self._spawning = True
        self._ensure_drops()
        self._pulse()
        self.set_interval(0.02, self._tick)

    def _pulse(self) -> None:
        if not self._pulsing:
            return
        self.styles.animate("opacity", value=0.25, duration=0.35, on_complete=self._pulse_back)

    def _pulse_back(self) -> None:
        if not self._pulsing:
            return
        self.styles.animate("opacity", value=1.0, duration=0.35, on_complete=self._pulse)

    def stop_pulse(self) -> None:
        self._pulsing = False

    def _ensure_drops(self) -> None:
        width, height = max(1, self.size.width), max(1, self.size.height)
        if (width, height) == self._last_size:
            return
        self._last_size = (width, height)
        count = max(12, width // 2)
        self._drops = [self._new_drop(width, height) for _ in range(count)]

    def _new_drop(self, width: int, height: int) -> dict:
        length = randint(4, 10)
        return {
            "x": randint(0, max(0, width - 1)),
            "y": random() * height * -1.0,
            "speed": 0.45 + random() * 0.3,
            "length": length,
            "offset": randint(0, len(self.RAIN_COLORS) - 1),
        }

    def _tick(self) -> None:
        self._ensure_drops()
        width, height = self._last_size
        for drop in self._drops:
            drop["y"] += drop["speed"]
            if drop["y"] - drop["length"] > height:
                if self._spawning:
                    drop.update(self._new_drop(width, height))
                else:
                    drop["y"] = height + drop["length"] + 1
                    drop["speed"] = 0.0
        self.refresh()
    def stop_rain(self) -> None:
        self._spawning = False

    @staticmethod
    def _ease_in_out_expo(t: float) -> float:
        if t <= 0.0:
            return 0.0
        if t >= 1.0:
            return 1.0
        if t < 0.5:
            return pow(2, 20 * t - 10) / 2
        return (2 - pow(2, -20 * t + 10)) / 2

    def _animated_bar(self, base_line: str) -> str:
        base_len = len(base_line)
        if base_len <= 0:
            return base_line
        period = 2.4
        phase = (time.monotonic() % period) / period
        triangle = 1.0 - abs(2.0 * phase - 1.0)
        eased = self._ease_in_out_expo(triangle)
        min_len = max(6, int(base_len * 0.35))
        length = int(min_len + (base_len - min_len) * eased)
        pad_left = (base_len - length) // 2
        pad_right = base_len - length - pad_left
        return (" " * pad_left) + ("=" * length) + (" " * pad_right)

    def render(self) -> Text:
        width, height = self._last_size
        width = max(1, width)
        height = max(1, height)
        lines = [list(" " * width) for _ in range(height)]
        styles: dict[int, str] = {}

        for drop in self._drops:
            head = int(drop["y"])
            palette = self.RAIN_COLORS[drop["offset"] :] + self.RAIN_COLORS[: drop["offset"]]
            for i in range(drop["length"]):
                y = head - i
                if 0 <= y < height:
                    x = drop["x"]
                    lines[y][x] = "█"
                    color = palette[min(i, len(palette) - 1)]
                    styles[y * (width + 1) + x] = color

        art_lines = SPLASH.strip("\n").splitlines()
        if art_lines:
            for idx, line in enumerate(art_lines):
                if line.strip() and set(line.strip()) == {"="}:
                    art_lines[idx] = self._animated_bar(line)
            art_height = len(art_lines)
            art_width = max(len(line) for line in art_lines)
            start_y = max(0, (height - art_height) // 2)
            start_x = max(0, (width - art_width) // 2)
            for row, line in enumerate(art_lines):
                y = start_y + row
                if y >= height:
                    break
                for col, ch in enumerate(line):
                    if ch == " ":
                        continue
                    x = start_x + col
                    if 0 <= x < width:
                        lines[y][x] = ch
                        styles[y * (width + 1) + x] = "#ffb347"

        text = Text("\n".join("".join(line) for line in lines))
        for index, color in styles.items():
            text.stylize(color, index, index + 1)
        return text

class HomeWanderer(Static):
    _MESSAGES = [
        "ssh in",
        "tap [r]",
        "build > run",
        "wire it",
        "ship it",
        "secure it",
    ]

    def on_mount(self) -> None:
        self._x = 0
        self._y = 0
        self._dx = 1
        self._step = 0
        self._msg = choice(self._MESSAGES)
        self.set_interval(0.09, self._tick)

    def _tick(self) -> None:
        width = max(1, self.size.width)
        height = max(1, self.size.height)
        if self._step % 6 == 0:
            self._dx = choice([1, -1])
        if self._step % 18 == 0:
            self._msg = choice(self._MESSAGES)
        self._x = (self._x + self._dx) % width
        self._step += 1
        self.refresh()

    def render(self) -> Text:
        width = max(10, self.size.width)
        height = max(2, self.size.height)
        lines = [list(" " * width) for _ in range(height)]
        guy = "<o/"
        gx = min(self._x, width - len(guy))
        for i, ch in enumerate(guy):
            x = gx + i
            if 0 <= x < width:
                lines[1][x] = ch
        msg = f"[{self._msg}]"
        mx = (gx + len(guy) + 1) % width
        if mx + len(msg) >= width:
            mx = max(0, width - len(msg))
        for i, ch in enumerate(msg):
            x = mx + i
            if 0 <= x < width:
                lines[0][x] = ch
        text = Text("\n".join("".join(line) for line in lines))
        text.stylize("#ff8a00")
        return text

class HomeTicker(Static):
    _TEXT = "aidanek.dev :: ssh in :: press [h] [r] [q] :: "

    def on_mount(self) -> None:
        self._offset = 0
        self.set_interval(0.06, self._tick)

    def _tick(self) -> None:
        self._offset = (self._offset + 1) % len(self._TEXT)
        self.refresh()

    def render(self) -> Text:
        width = max(10, self.size.width)
        slice_text = (self._TEXT * ((width // len(self._TEXT)) + 2))
        start = self._offset % len(self._TEXT)
        line = slice_text[start : start + width]
        text = Text(line)
        text.stylize("#ffb347")
        return text

class HomeSparks(Static):
    def on_mount(self) -> None:
        self._tick_count = 0
        self.set_interval(0.12, self._tick)

    def _tick(self) -> None:
        self._tick_count += 1
        self.refresh()

    def render(self) -> Text:
        width = max(10, self.size.width)
        height = max(2, self.size.height)
        lines = [list(" " * width) for _ in range(height)]
        for _ in range(max(6, width // 6)):
            x = randint(0, width - 1)
            y = randint(0, height - 1)
            lines[y][x] = choice([".", "+", "*"])
        if random() < 0.3:
            emote = choice(["(>_<)", "(o_o)", "(-_-)", "o/"])
            if len(emote) <= width:
                ex = randint(0, width - len(emote))
                ey = randint(0, height - 1)
                for i, ch in enumerate(emote):
                    lines[ey][ex + i] = ch
        text = Text("\n".join("".join(line) for line in lines))
        text.stylize("#ffd7a6")
        return text

class HomeFingerprint(Static):
    _TEXT = (
        "ED25519 key fingerprint is SHA256:74WCiLMpyIPrysNUwu1WAc4DjhtyRxUDRTCV71oFvZw.\n"
        "This key is not known by any other names.\n"
        "Are you sure you want to continue connecting (yes/no/[fingerprint])?"
    )

    def render(self) -> Text:
        text = Text(self._TEXT)
        text.stylize("#3a3a3a")
        return text

class HomeYesPrompt(Static):
    _PROMPT = "$ "
    _WORD = "yes"

    def on_mount(self) -> None:
        self._index = 0
        self._pause = 0
        self._cursor_on = True
        self._entered = False
        self.set_interval(0.12, self._tick)
        self.set_interval(0.4, self._blink)

    def _tick(self) -> None:
        if self._index < len(self._WORD):
            self._index += 1
        else:
            self._pause += 1
            if not self._entered and self._pause > 6:
                self._entered = True
                self._pause = 0
            elif self._entered and self._pause > 10:
                self._index = 0
                self._pause = 0
                self._entered = False
        self.refresh()

    def _blink(self) -> None:
        self._cursor_on = not self._cursor_on
        self.refresh()

    def render(self) -> Text:
        typed = self._WORD[: self._index]
        cursor = "█" if self._cursor_on else " "
        if self._entered:
            text = Text(f"{self._PROMPT}{self._WORD}\n{self._PROMPT}{cursor}")
            first_line_len = len(self._PROMPT) + len(self._WORD)
            second_line_offset = first_line_len + 1  # newline
            text.stylize("#ffffff", 0, len(self._PROMPT))
            text.stylize(ACCENT_COLOR, len(self._PROMPT), first_line_len)
            text.stylize("#ffffff", second_line_offset, second_line_offset + len(self._PROMPT))
        else:
            text = Text(self._PROMPT + typed + cursor)
            text.stylize("#ffffff", 0, len(self._PROMPT))
            text.stylize(ACCENT_COLOR, len(self._PROMPT), len(self._PROMPT) + len(typed))
        return text

class HomeTypewriter(Static):
    _MESSAGE = "Welcome to aidanek.dev!"

    def on_mount(self) -> None:
        self._index = 0
        self._cursor_on = True
        self.set_interval(0.08, self._tick)
        self.set_interval(0.4, self._blink)

    def _tick(self) -> None:
        if self._index < len(self._MESSAGE):
            self._index += 1
        self.refresh()

    def _blink(self) -> None:
        self._cursor_on = not self._cursor_on
        self.refresh()

    def render(self) -> Text:
        width = max(10, self.size.width)
        typed = self._MESSAGE[: self._index]
        cursor = "█" if self._cursor_on else " "
        line = (typed + cursor).ljust(width)
        text = Text(line)
        text.stylize("#ffb347")
        return text

class SshSite(App):
    TITLE="aidanek.dev"
    SUB_TITLE="home"
    CSS = """
    Screen {
        overflow: hidden;
    }

    #splash {
        dock: top;
        height: 1fr;
        width: 100%;
        background: $background;
        color: $foreground;
    }

    #body {
        overflow: hidden;
    }

    #body_text {
        padding: 1 2;
    }

    #home_view {
        padding: 1 2;
        height: 1fr;
        display: none;
        align: center middle;
    }

    #home_help {
        padding: 0 2;
        margin: 0;
        text-style: bold;
    }

    #home_title {
        border: wide $primary;
        padding: 1 4;
        margin: 0;
        text-style: bold;
        background: $panel;
    }

    #home_panels {
        height: auto;
        width: 100%;
        align: center middle;
    }

    #home_ticker {
        border: wide $secondary;
        padding: 1 2;
        margin: 0;
        text-style: bold;
    }


    #home_sparks {
        padding: 0 2;
        margin: 0;
        height: 3;
    }

    #home_fingerprint {
        padding: 1 2;
        margin: 0;
    }

    #home_yes {
        padding: 0 2;
        margin: 0;
    }

    #home_sparks {
        padding: 0 2;
        margin: 1 0 0 0;
        height: 3;
    }

    .home_panel {
        border: wide $secondary;
        padding: 1 2;
        margin: 0 1;
        width: 1fr;
        height: auto;
    }

    #home_pulse {
        border: wide $accent;
        padding: 1 2;
        margin: 0;
        text-align: center;
    }

    .tab_button {
        border: wide $primary;
        background: $panel;
        color: $foreground;
        padding: 1 4;
        margin: 0 1;
        text-style: bold;
        width: 1fr;
        height: auto;
        content-align: center middle;
    }

    .tab_button.is-active {
        background: $accent;
        color: $background;
    }

    .tab_button:hover {
        background: $boost;
        color: $foreground;
    }

    #nav_bar {
        height: auto;
        padding: 0 1;
        background: transparent;
        align: center middle;
    }

    #resume_view {
        padding: 0 2;
        display: none;
        height: 1fr;
        overflow: auto;
    }

    #resume_name {
        border: wide $primary;
        padding: 1 4;
        margin: 0;
    }

    #resume_skills {
        border: wide $secondary;
        padding: 1 2;
        margin: 0;
    }

    #resume_projects {
        border: wide $secondary;
        padding: 1 2;
        margin: 0;
    }

    #resume_pdf {
        padding: 0 1;
        margin: 0 0 1 0;
    }
    """

    BINDINGS = [
        Binding("h", "home", "Home"),
        Binding("question_mark", "help", "Help"),
        Binding("r", "resume", "Resume"),
        Binding("ctrl+p", "command_palette", "Search", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        self.body_text = Static(HOME, id="body_text")
        self.home_view = Vertical(
            Static("press (?) for help", id="home_help"),
            HomeTypewriter(id="home_title"),
            HomeTicker(id="home_ticker"),
            HomeWanderer(id="home_pulse"),
            HomeFingerprint(id="home_fingerprint"),
            HomeYesPrompt(id="home_yes"),
            HomeSparks(id="home_sparks"),
            id="home_view",
        )
        resume_link = "https://aidanek.dev/resume.pdf"
        skills_title = "Skills"
        skills_text = Text(
            f"{skills_title}\n\nPython, Java, C, Linux, Server Hardening, Binary Exploitation"
        )
        skills_text.stylize(ACCENT_COLOR, 0, len(skills_title))
        projects_title = "Projects"
        projects_text = Text(
            f"{projects_title}\n\n- aidanek.dev interactive portfolio (asyncssh, Textual)\n"
            "\n- SSH config command line utility"
        )
        projects_text.stylize(ACCENT_COLOR, 0, len(projects_title))
        name_text = Text("Aidan Elliott-Korytek\nSecurity · Systems · Networking")
        name_text.stylize(ACCENT_COLOR, 0, len("Aidan Elliott-Korytek"))
        resume_pdf_text = Text(f"Full resume (PDF): {resume_link}")
        resume_pdf_title = "Full resume (PDF)"
        resume_pdf_text.stylize(ACCENT_COLOR, 0, len(resume_pdf_title))
        link_start = resume_pdf_text.plain.find(resume_link)
        if link_start != -1:
            resume_pdf_text.stylize(
                f"link {resume_link}",
                link_start,
                link_start + len(resume_link),
            )
        self.resume_view = Vertical(
            Static(name_text, id="resume_name"),
            Static(skills_text, id="resume_skills"),
            Static(projects_text, id="resume_projects"),
            Static(resume_pdf_text, id="resume_pdf"),
            id="resume_view",
        )
        self.nav_bar = Horizontal(
            Button("home (h)", id="nav_home", classes="tab_button"),
            Button("resume (r)", id="nav_resume", classes="tab_button"),
            Button("quit (q)", id="nav_quit", classes="tab_button"),
            id="nav_bar",
        )
        self.body = Vertical(self.nav_bar, self.home_view, self.body_text, self.resume_view, id="body")
        self.splash = RainSplash(id="splash")
        yield self.splash
        yield self.body

    def on_mount(self) -> None:
        self.register_theme(THEME)
        self.theme = "aidanek"
        self.body.display = False
        self._splash_duration = 5.0
        self.set_timer(self._splash_duration, self._dismiss_splash)

    def _dismiss_splash(self) -> None:
        self.splash.stop_pulse()
        self.splash.stop_rain()
        self.splash.styles.animate(
            "opacity",
            value=0.0,
            duration=0.6,
            on_complete=self._hide_splash,
        )
        self.set_timer(1.0, self._show_main)

    def _hide_splash(self) -> None:
        self.splash.display = False

    def _show_main(self) -> None:
        self.body.display = True
        self.action_home()

    def _set_active_nav(self, active_id: str | None) -> None:
        for button_id in ("nav_home", "nav_resume"):
            button = self.query_one(f"#{button_id}", Button)
            button.set_class(button_id == active_id, "is-active")

    def _show_body_text(self, content: str) -> None:
        self.body_text.update(content)
        self.body_text.display = True
        self.resume_view.display = False
        self.home_view.display = False
        self._set_active_nav(None)
        self.body_text.styles.text_align = "left"
        self.body_text.styles.border = None
        self.body_text.styles.padding = (1, 2)

    def _show_home(self) -> None:
        self.home_view.display = True
        self.body_text.display = False
        self.resume_view.display = False

    def action_home(self) -> None:
        self.sub_title = "home"
        self._show_home()
        self._set_active_nav("nav_home")

    def action_help(self) -> None:
        self.sub_title = "help"
        help_text = Text(HELP)
        offset = 0
        for line in HELP.splitlines():
            if line.startswith("h ·"):
                help_text.stylize(ACCENT_COLOR, offset, offset + 1)
            elif line.startswith("? ·"):
                help_text.stylize(ACCENT_COLOR, offset, offset + 1)
            elif line.startswith("r ·"):
                help_text.stylize(ACCENT_COLOR, offset, offset + 1)
            elif line.startswith("^p ·"):
                help_text.stylize(ACCENT_COLOR, offset, offset + 2)
            elif line.startswith("q ·"):
                help_text.stylize(ACCENT_COLOR, offset, offset + 1)
            offset += len(line) + 1
        self._show_body_text(help_text)
        self.body_text.styles.text_align = "center"
        self.body_text.styles.border = ("wide", ACCENT_COLOR)
        self.body_text.styles.padding = (1, 3)

    def action_resume(self) -> None:
        self.sub_title = "resume"
        self.body_text.display = False
        self.home_view.display = False
        self.resume_view.display = True
        self._set_active_nav("nav_resume")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "nav_home":
            self._set_active_nav("nav_home")
            self.action_home()
        elif event.button.id == "nav_resume":
            self._set_active_nav("nav_resume")
            self.action_resume()
        elif event.button.id == "nav_quit":
            self.exit()

    def get_system_commands(self, screen) -> Iterable[SystemCommand]:
        yield SystemCommand("Home", "Go to the home screen", self.action_home)
        yield SystemCommand("Help", "Show help", self.action_help)
        yield SystemCommand("Resume", "Show the resume", self.action_resume)
        yield SystemCommand("Quit", "Exit the app", self.exit)

if __name__ == "__main__":
    SshSite().run()
