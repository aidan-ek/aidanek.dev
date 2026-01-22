from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding

HOME = "Welcome to aidanek.dev\n\nPress ? for help\n"

HELP = """Keybinds
h  Home
?  Help
q  Quit
"""

class SshSite(App):
    BINDINGS = [
        Binding("h", "home", "Home"),
        Binding("question_mark", "help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        self.body = Static(HOME)
        yield self.body
        yield Footer()

    def action_home(self) -> None:
        self.body.update(HOME)

    def action_help(self) -> None:
        self.body.update(HELP)

if __name__ == "__main__":
    SshSite().run()
