"""Todo app help screen module."""
from pathlib import Path
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Markdown


class TodoHelp(Markdown):
    """Markdown help."""

    async def on_mount(self) -> None:
        path = Path() / 'README.md'
        await self.load(path)


class HelpScreen(Screen):
    """Help screen."""
    BINDINGS = [
            Binding('escape', 'quit_help', 'quit', show=False),
            Binding('q', 'quit_help', 'quit', show=False),
            ]
    def compose(self) -> ComposeResult:
        yield TodoHelp()

    def action_quit_help(self) -> None:
        """Quit help"""
        self.app.switch_mode('home')
