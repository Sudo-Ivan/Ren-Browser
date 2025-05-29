import flet as ft

def render_micron(content: str) -> ft.Control:
    """
    Render micron markup content to a Flet control placeholder.
    Currently displays raw content.
    """
    return ft.Text(
        content,
        selectable=True,
        font_family="monospace",
        expand=True,
    )