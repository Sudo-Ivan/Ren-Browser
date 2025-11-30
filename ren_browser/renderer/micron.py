"""Micron markup renderer for Ren Browser.

Provides rendering capabilities for micron markup content.
"""

import re

import flet as ft

from ren_browser.renderer.plaintext import render_plaintext


def hex_to_rgb(hex_color: str) -> str:
    """Convert 3-char hex color to RGB string."""
    if len(hex_color) != 3:
        return "255,255,255"
    r = int(hex_color[0], 16) * 17
    g = int(hex_color[1], 16) * 17
    b = int(hex_color[2], 16) * 17
    return f"{r},{g},{b}"


def parse_micron_line(line: str) -> list:
    """Parse a single line of micron markup into styled text spans.

    Returns list of dicts with 'text', 'bold', 'italic', 'underline', 'color', 'bgcolor'.
    """
    spans = []
    current_text = ""
    bold = False
    italic = False
    underline = False
    color = None
    bgcolor = None

    i = 0
    while i < len(line):
        if line[i] == "`" and i + 1 < len(line):
            if current_text:
                spans.append(
                    {
                        "text": current_text,
                        "bold": bold,
                        "italic": italic,
                        "underline": underline,
                        "color": color,
                        "bgcolor": bgcolor,
                    },
                )
                current_text = ""

            tag = line[i + 1]

            if tag == "!":
                bold = not bold
                i += 2
            elif tag == "*":
                italic = not italic
                i += 2
            elif tag == "_":
                underline = not underline
                i += 2
            elif tag == "F" and i + 5 <= len(line):
                color = hex_to_rgb(line[i + 2 : i + 5])
                i += 5
            elif tag == "f":
                color = None
                i += 2
            elif tag == "B" and i + 5 <= len(line):
                bgcolor = hex_to_rgb(line[i + 2 : i + 5])
                i += 5
            elif tag == "b":
                bgcolor = None
                i += 2
            elif tag == "`":
                bold = False
                italic = False
                underline = False
                color = None
                bgcolor = None
                i += 2
            else:
                current_text += line[i]
                i += 1
        else:
            current_text += line[i]
            i += 1

    if current_text:
        spans.append(
            {
                "text": current_text,
                "bold": bold,
                "italic": italic,
                "underline": underline,
                "color": color,
                "bgcolor": bgcolor,
            },
        )

    return spans


def render_micron(content: str, on_link_click=None) -> ft.Control:
    """Render micron markup content to a Flet control.

    Falls back to plaintext renderer if parsing fails.

    Args:
        content: Micron markup content to render.
        on_link_click: Optional callback function(url) called when a link is clicked.

    Returns:
        ft.Control: Rendered content as a Flet control.

    """
    try:
        return _render_micron_internal(content, on_link_click)
    except Exception as e:
        print(f"Micron rendering failed: {e}, falling back to plaintext")
        return render_plaintext(content)


def _render_micron_internal(content: str, on_link_click=None) -> ft.Control:
    """Internal micron rendering implementation.

    Args:
        content: Micron markup content to render.
        on_link_click: Optional callback function(url) called when a link is clicked.

    Returns:
        ft.Control: Rendered content as a Flet control.

    """
    lines = content.split("\n")
    controls = []
    section_level = 0
    alignment = ft.TextAlign.LEFT

    for line in lines:
        if not line:
            controls.append(ft.Container(height=10))
            continue

        if line.startswith("#"):
            continue

        if line.startswith("`c"):
            alignment = ft.TextAlign.CENTER
            line = line[2:]
        elif line.startswith("`l"):
            alignment = ft.TextAlign.LEFT
            line = line[2:]
        elif line.startswith("`r"):
            alignment = ft.TextAlign.RIGHT
            line = line[2:]
        elif line.startswith("`a"):
            alignment = ft.TextAlign.LEFT
            line = line[2:]

        if line.startswith(">"):
            level = 0
            while level < len(line) and line[level] == ">":
                level += 1
            section_level = level
            heading_text = line[level:].strip()

            if heading_text:
                controls.append(
                    ft.Container(
                        content=ft.Text(
                            heading_text,
                            size=20 - (level * 2),
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_400,
                        ),
                        padding=ft.padding.only(left=level * 20, top=10, bottom=5),
                    ),
                )
            continue

        if line.strip() == "-":
            controls.append(
                ft.Container(
                    content=ft.Divider(color=ft.Colors.GREY_700),
                    padding=ft.padding.only(left=section_level * 20),
                ),
            )
            continue

        if "`[" in line:
            row_controls = []
            last_end = 0

            for link_match in re.finditer(r"`\[([^`]*)`([^\]]*)\]", line):
                before = line[last_end : link_match.start()]
                if before:
                    before_spans = parse_micron_line(before)
                    row_controls.extend(
                        create_text_span(span) for span in before_spans
                    )

                label = link_match.group(1)
                url = link_match.group(2)

                def make_link_handler(link_url):
                    def handler(e):
                        if on_link_click:
                            on_link_click(link_url)

                    return handler

                row_controls.append(
                    ft.TextButton(
                        text=label if label else url,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_400,
                            overlay_color=ft.Colors.BLUE_900,
                        ),
                        on_click=make_link_handler(url),
                    ),
                )

                last_end = link_match.end()

            after = line[last_end:]
            if after:
                after_spans = parse_micron_line(after)
                row_controls.extend(
                    create_text_span(span) for span in after_spans
                )

            if row_controls:
                controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=row_controls,
                            spacing=0,
                            wrap=True,
                        ),
                        padding=ft.padding.only(left=section_level * 20),
                    ),
                )
                continue

        spans = parse_micron_line(line)
        if spans:
            text_controls = [create_text_span(span) for span in spans]

            controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=text_controls,
                        spacing=0,
                        wrap=True,
                        alignment=alignment,
                    ),
                    padding=ft.padding.only(left=section_level * 20),
                ),
            )

    return ft.Column(
        controls=controls,
        spacing=5,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def create_text_span(span: dict) -> ft.Text:
    """Create a Text control from a span dict."""
    styles = []
    if span["bold"]:
        styles.append(ft.TextStyle(weight=ft.FontWeight.BOLD))
    if span["italic"]:
        styles.append(ft.TextStyle(italic=True))

    text_decoration = ft.TextDecoration.UNDERLINE if span["underline"] else None
    color = span["color"]
    bgcolor = span["bgcolor"]

    text_style = ft.TextStyle(
        weight=ft.FontWeight.BOLD if span["bold"] else None,
        italic=span["italic"] if span["italic"] else None,
        decoration=text_decoration,
    )

    return ft.Text(
        span["text"],
        style=text_style,
        color=f"rgb({color})" if color else None,
        bgcolor=f"rgb({bgcolor})" if bgcolor else None,
        selectable=True,
        no_wrap=False,
    )
