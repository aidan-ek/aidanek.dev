from random import randint, random
import time
from typing import Iterable

from rich.text import Text
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.theme import Theme

from textual.widgets import Header, Footer, Static

HOME = """Welcome to aidanek.dev\n\nPress ? for help\n

       .__    .___                     __            .___           
_____  |__| __| _/____    ____   ____ |  | __      __| _/_______  __
\__  \ |  |/ __ |\__  \  /    \_/ __ \|  |/ /     / __ |/ __ \  \/ /
 / __ \|  / /_/ | / __ \|   |  \  ___/|    <     / /_/ \  ___/\   / 
(____  /__\____ |(____  /___|  /\___  >__|_ \ /\ \____ |\___  >\_/  
     \/        \/     \/     \/     \/     \/ \/      \/    \/     
     
     
"""

HELP = """Keybinds
h  Home
?  Help
q  Quit
"""

SPLASH = """
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

class SshSite(App):
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
    """

    BINDINGS = [
        Binding("h", "home", "Home"),
        Binding("question_mark", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        self.header = Header(show_clock=True)
        self.footer = Footer()
        self.body = Static(HOME, id="body")
        self.splash = RainSplash(id="splash")
        yield self.header
        yield self.splash
        yield self.body
        yield self.footer

    def on_mount(self) -> None:
        self.register_theme(THEME)
        self.theme = "aidanek"
        self.header.display = False
        self.footer.display = False
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
        self.header.display = True
        self.footer.display = True
        self.body.display = True

    def action_home(self) -> None:
        self.body.update(HOME)

    def action_help(self) -> None:
        self.body.update(HELP)

    def get_system_commands(self, screen) -> Iterable[SystemCommand]:
        yield SystemCommand("Quit", "Exit the app", self.exit)

if __name__ == "__main__":
    SshSite().run()
