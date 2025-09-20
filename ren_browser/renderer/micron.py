"""Micron markup renderer for Ren Browser.

Provides rendering capabilities for micron markup content,
currently implemented as a placeholder.
"""
import flet as ft


def render_micron(content: str) -> ft.Control:
    """Render micron markup content to a Flet control placeholder.

    Currently displays raw content.

    Args:
        content: Micron markup content to render.

    Returns:
        ft.Control: Rendered content as a Flet control.

    """
    return ft.Text(
        content,
        selectable=True,
        font_family="monospace",
        expand=True,
    )
