from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding

HOME = """Welcome to aidanek.dev\n\nPress ? for help\n


    .              .oooo.   oooo
  .o8            .dP""Y88b  `888
.o888oo oooo d8b       ]8P'  888  oooo
  888   `888""8P     <88b.   888 .8P'
  888    888          `88b.  888888.
  888 .  888     o.   .88P   888 `88b.
  "888" d888b    `8bd88P'   o888o o888o

"""

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
