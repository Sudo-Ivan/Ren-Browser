import flet as ft


def render_plaintext(content: str) -> ft.Control:
    """Fallback plaintext renderer: displays raw text safely in a monospace, selectable control.
    """
    return ft.Text(
        content,
        selectable=True,
        font_family="monospace",
        expand=True,
    )
