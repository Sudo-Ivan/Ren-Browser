"""Micron markup renderer for Ren Browser.

Provides rendering capabilities for micron markup content,
currently implemented as a placeholder.
"""

import re

import flet as ft


class MicronParser:
    """Parses micron markup and converts it to Flet controls.

    Supports headings, dividers, inline formatting, ASCII art detection,
    and color/formatting codes.
    """

    def __init__(self, dark_theme=True, enable_force_monospace=True, ascii_art_scale=0.75):
        """Initialize the MicronParser.

        Args:
            dark_theme (bool): Whether to use dark theme styles.
            enable_force_monospace (bool): If True, force monospace font.
            ascii_art_scale (float): Scale factor for ASCII art font size.

        """
        self.dark_theme = dark_theme
        self.enable_force_monospace = enable_force_monospace
        self.ascii_art_scale = ascii_art_scale
        self.DEFAULT_FG_DARK = "ddd"
        self.DEFAULT_FG_LIGHT = "222"
        self.DEFAULT_BG = "default"

        self.SELECTED_STYLES = None

        self.STYLES_DARK = {
            "plain": {"fg": self.DEFAULT_FG_DARK, "bg": self.DEFAULT_BG, "bold": False, "underline": False, "italic": False},
            "heading1": {"fg": "000", "bg": "bbb", "bold": True, "underline": False, "italic": False},
            "heading2": {"fg": "000", "bg": "999", "bold": True, "underline": False, "italic": False},
            "heading3": {"fg": "fff", "bg": "777", "bold": True, "underline": False, "italic": False},
        }

        self.STYLES_LIGHT = {
            "plain": {"fg": self.DEFAULT_FG_LIGHT, "bg": self.DEFAULT_BG, "bold": False, "underline": False, "italic": False},
            "heading1": {"fg": "fff", "bg": "777", "bold": True, "underline": False, "italic": False},
            "heading2": {"fg": "000", "bg": "aaa", "bold": True, "underline": False, "italic": False},
            "heading3": {"fg": "000", "bg": "ccc", "bold": True, "underline": False, "italic": False},
        }

        if self.dark_theme:
            self.SELECTED_STYLES = self.STYLES_DARK
        else:
            self.SELECTED_STYLES = self.STYLES_LIGHT

    def convert_micron_to_controls(self, markup: str) -> list[ft.Control]:
        """Convert micron markup to a list of Flet controls.

        Args:
            markup (str): The micron markup string.

        Returns:
            list[ft.Control]: List of Flet controls representing the markup.

        """
        controls = []
        state = self._init_state()
        lines = markup.split("\n")

        for line in lines:
            line_controls = self._parse_line(line, state)
            if line_controls:
                controls.extend(line_controls)

        return controls

    def _init_state(self) -> dict:
        """Initialize the parsing state for a new document.

        Returns:
            dict: The initial state dictionary.

        """
        return {
            "literal": False,
            "depth": 0,
            "fg_color": self.SELECTED_STYLES["plain"]["fg"],
            "bg_color": self.DEFAULT_BG,
            "formatting": {
                "bold": False,
                "underline": False,
                "italic": False,
            },
            "default_align": "left",
            "align": "left",
        }

    def _parse_line(self, line: str, state: dict) -> list[ft.Control]:
        """Parse a single line of micron markup.

        Args:
            line (str): The line to parse.
            state (dict): The current parsing state.

        Returns:
            list[ft.Control]: Controls for this line, or empty if none.

        """
        if not line:
            return []

        if line == "`=":
            state["literal"] = not state["literal"]
            return []

        if not state["literal"] and line.startswith("#"):
            return []

        if not state["literal"] and line.startswith("<"):
            state["depth"] = 0
            return self._parse_line(line[1:], state)

        if not state["literal"] and line.startswith(">"):
            return self._parse_heading(line, state)

        if not state["literal"] and line.startswith("-"):
            return self._parse_divider(line, state)

        return self._parse_inline_formatting(line, state)

    def _parse_inline_formatting(self, line: str, state: dict) -> list[ft.Control]:
        """Parse inline formatting codes in a line and return Flet controls.

        Args:
            line (str): The line to parse.
            state (dict): The current parsing state.

        Returns:
            list[ft.Control]: Controls for the formatted line.

        """
        spans = []
        current_text = ""
        current_style = {
            "fg": state["fg_color"],
            "bg": state["bg_color"],
            "bold": state["formatting"]["bold"],
            "underline": state["formatting"]["underline"],
            "italic": state["formatting"]["italic"],
        }

        mode = "text"
        i = 0
        skip = 0

        def flush_current():
            """Flush the current text buffer into a span."""
            nonlocal current_text
            if current_text:
                spans.append(MicronParser._create_span(current_text, current_style))
                current_text = ""

        while i < len(line):
            if skip > 0:
                skip -= 1
                i += 1
                continue

            char = line[i]
            """
            Handle backticks for formatting:
            - Double backtick (``) resets formatting and alignment.
            - Single backtick toggles formatting mode.
            """
            if char == "`":
                flush_current()
                if i + 1 < len(line) and line[i + 1] == "`":
                    current_style["bold"] = False
                    current_style["underline"] = False
                    current_style["italic"] = False
                    current_style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
                    current_style["bg"] = self.DEFAULT_BG
                    state["align"] = state["default_align"]
                    i += 2
                    continue
                mode = "formatting" if mode == "text" else "text"
                i += 1
                continue

            if mode == "formatting":
                handled = False
                if char == "_":
                    current_style["underline"] = not current_style["underline"]
                    handled = True
                elif char == "!":
                    current_style["bold"] = not current_style["bold"]
                    handled = True
                elif char == "*":
                    current_style["italic"] = not current_style["italic"]
                    handled = True
                elif char == "F":
                    if len(line) >= i + 4:
                        current_style["fg"] = line[i + 1:i + 4]
                        skip = 3
                    handled = True
                elif char == "f":
                    current_style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
                    handled = True
                elif char == "B":
                    if len(line) >= i + 4:
                        current_style["bg"] = line[i + 1:i + 4]
                        skip = 3
                    handled = True
                elif char == "b":
                    current_style["bg"] = self.DEFAULT_BG
                    handled = True
                elif char == "c":
                    state["align"] = "center"
                    handled = True
                elif char == "l":
                    state["align"] = "left"
                    handled = True
                elif char == "r":
                    state["align"] = "right"
                    handled = True
                elif char == "a":
                    state["align"] = state["default_align"]
                    handled = True

                if not handled:
                    current_text += char

            else:
                current_text += char
            i += 1

        flush_current()

        if spans:
            is_art = MicronParser._is_ascii_art("".join(span.text for span in spans))
            font_size = 12 * self.ascii_art_scale if is_art else None
            text_control = ft.Text(spans=spans, text_align=state["align"], selectable=True, enable_interactive_selection=True, expand=True, font_family="monospace", size=font_size)
        else:
            is_art = MicronParser._is_ascii_art(line)
            font_size = 12 * self.ascii_art_scale if is_art else None
            text_control = ft.Text(line, text_align=state["align"], selectable=True, enable_interactive_selection=True, expand=True, font_family="monospace", size=font_size)

        if state["depth"] > 0:
            indent_em = (state["depth"] - 1) * 1.2
            text_control = ft.Container(
                content=text_control,
                margin=ft.margin.only(left=indent_em * 16),
            )

        return [text_control]

    @staticmethod
    def _create_span(text: str, style: dict) -> ft.TextSpan:
        """Create a Flet TextSpan with the given style.

        Args:
            text (str): The text for the span.
            style (dict): The style dictionary.

        Returns:
            ft.TextSpan: The styled text span.

        """
        flet_style = ft.TextStyle(
            color=MicronParser._color_to_flet(style["fg"]),
            bgcolor=MicronParser._color_to_flet(style["bg"]),
            weight=ft.FontWeight.BOLD if style["bold"] else ft.FontWeight.NORMAL,
            decoration=ft.TextDecoration.UNDERLINE if style["underline"] else ft.TextDecoration.NONE,
            italic=style["italic"],
        )
        return ft.TextSpan(text, flet_style)

    def _apply_format_code_to_style(self, code: str, style: dict, state: dict):
        """Apply a micron format code to a style dictionary.

        Args:
            code (str): The format code.
            style (dict): The style dictionary to modify.
            state (dict): The current parsing state.

        """
        if not code:
            return

        if code == "`":
            style["bold"] = False
            style["underline"] = False
            style["italic"] = False
            style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
            style["bg"] = self.DEFAULT_BG
            return

        if "!" in code:
            style["bold"] = not style["bold"]
        if "_" in code:
            style["underline"] = not style["underline"]
        if "*" in code:
            style["italic"] = not style["italic"]

        if code.startswith("F") and len(code) >= 4:
            style["fg"] = code[1:4]
        elif code.startswith("B") and len(code) >= 4:
            style["bg"] = code[1:4]

        if "f" in code:
            style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
        if "b" in code:
            style["bg"] = self.DEFAULT_BG

    def _apply_format_code(self, code: str, state: dict):
        """Apply a micron format code to the parsing state.

        Args:
            code (str): The format code.
            state (dict): The state dictionary to modify.

        """
        if not code:
            return

        if code == "`":
            state["formatting"]["bold"] = False
            state["formatting"]["underline"] = False
            state["formatting"]["italic"] = False
            state["fg_color"] = self.SELECTED_STYLES["plain"]["fg"]
            state["bg_color"] = self.DEFAULT_BG
            state["align"] = state["default_align"]
            return

        if "!" in code:
            state["formatting"]["bold"] = not state["formatting"]["bold"]
        if "_" in code:
            state["formatting"]["underline"] = not state["formatting"]["underline"]
        if "*" in code:
            state["formatting"]["italic"] = not state["formatting"]["italic"]

        if code.startswith("F") and len(code) >= 4:
            state["fg_color"] = code[1:4]
        elif code.startswith("B") and len(code) >= 4:
            state["bg_color"] = code[1:4]

        if "f" in code:
            state["fg_color"] = self.SELECTED_STYLES["plain"]["fg"]
        if "b" in code:
            state["bg_color"] = self.DEFAULT_BG

        if "c" in code:
            state["align"] = "center"
        elif "l" in code:
            state["align"] = "left"
        elif "r" in code:
            state["align"] = "right"
        elif "a" in code:
            state["align"] = state["default_align"]

    def _parse_divider(self, line: str, state: dict) -> list[ft.Control]:
        """Parse a divider line and return a Flet Divider or styled Text.

        Args:
            line (str): The divider line.
            state (dict): The current parsing state.

        Returns:
            list[ft.Control]: Controls for the divider.

        """
        if len(line) == 1:
            return [ft.Divider()]
        divider_char = line[1] if len(line) > 1 else "-"
        repeated = divider_char * 80

        is_art = MicronParser._is_ascii_art(repeated)
        font_size = 12 * self.ascii_art_scale if is_art else None

        divider = ft.Text(
            repeated,
            font_family="monospace",
            color=MicronParser._color_to_flet(state["fg_color"]),
            bgcolor=MicronParser._color_to_flet(state["bg_color"]),
            no_wrap=True,
            overflow=ft.TextOverflow.CLIP,
            selectable=False,
            enable_interactive_selection=False,
            size=font_size,
        )

        return [divider]

    @staticmethod
    def _color_to_flet(color: str) -> str | None:
        """Convert micron color format to Flet color format.

        Args:
            color (str): The micron color string.

        Returns:
            str | None: The Flet color string or None if default/invalid.

        """
        if not color or color == "default":
            return None

        if len(color) == 3 and re.match(r"^[0-9a-fA-F]{3}$", color):
            return f"#{color[0]*2}{color[1]*2}{color[2]*2}"

        if len(color) == 6 and re.match(r"^[0-9a-fA-F]{6}$", color):
            return f"#{color}"

        if len(color) == 3 and color[0] == "g":
            try:
                val = int(color[1:])
                if 0 <= val <= 99:
                    h = hex(int(val * 2.55))[2:].zfill(2)
                    return f"#{h}{h}{h}"
            except ValueError:
                pass

        return None

    @staticmethod
    def _is_ascii_art(text: str) -> bool:
        """Detect if text appears to be ASCII art.

        Args:
            text (str): The text to check.

        Returns:
            bool: True if the text is likely ASCII art, False otherwise.

        """
        if not text or len(text) < 10:
            return False

        special_chars = set("│─┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬█▄▀▌▐■□▪▫▲▼◄►◆◇○●◎◢◣◥◤")
        special_count = sum(1 for char in text if char in special_chars or (ord(char) > 127))

        other_special = sum(1 for char in text if not char.isalnum() and char not in " \t")

        total_chars = len(text.replace(" ", "").replace("\t", ""))
        if total_chars == 0:
            return False

        special_ratio = (special_count + other_special) / total_chars
        return special_ratio > 0.3

    def _parse_heading(self, line: str, state: dict) -> list[ft.Control]:
        """Parse heading lines (starting with '>') and return styled controls.

        Args:
            line (str): The heading line.
            state (dict): The current parsing state.

        Returns:
            list[ft.Control]: Controls for the heading.

        """
        heading_level = 0
        for char in line:
            if char == ">":
                heading_level += 1
            else:
                break

        state["depth"] = heading_level

        heading_text = line[heading_level:].strip()

        if heading_text:
            style_key = f"heading{min(heading_level, 3)}"
            style = self.SELECTED_STYLES.get(style_key, self.SELECTED_STYLES["plain"])

            is_art = MicronParser._is_ascii_art(heading_text)
            base_size = 20 - heading_level * 2
            font_size = base_size * self.ascii_art_scale if is_art else base_size

            indent_em = max(0, (state["depth"] - 1) * 1.2)

            heading = ft.Text(
                heading_text,
                style=ft.TextStyle(
                    color=MicronParser._color_to_flet(style["fg"]),
                    weight=ft.FontWeight.BOLD if style["bold"] else ft.FontWeight.NORMAL,
                    size=font_size,
                ),
                selectable=True,
                enable_interactive_selection=True,
                expand=True,
                font_family="monospace",
            )

            bg_color = MicronParser._color_to_flet(style["bg"])
            if bg_color:
                heading = ft.Container(
                    content=ft.Container(
                        content=heading,
                        margin=ft.margin.only(left=indent_em * 16) if indent_em > 0 else None,
                        padding=ft.padding.symmetric(horizontal=4),
                    ),
                    bgcolor=bg_color,
                    width=float("inf"),
                )
            elif indent_em > 0:
                heading = ft.Container(
                    content=heading,
                    margin=ft.margin.only(left=indent_em * 16),
                    padding=ft.padding.symmetric(horizontal=4),
                )

            return [heading]

        return []


def render_micron(content: str, ascii_art_scale: float = 0.75) -> ft.Control:
    """Render micron markup content to a Flet control.

    Args:
        content: Micron markup content to render.
        ascii_art_scale: Scale factor for ASCII art (0.0-1.0). Default 0.75.

    Returns:
        ft.Control: Rendered content as a Flet control.

    This function parses the micron markup, merges adjacent text controls
    with the same style, and returns a Flet ListView containing the result.

    """
    parser = MicronParser(ascii_art_scale=ascii_art_scale)
    controls = parser.convert_micron_to_controls(content)

    merged_controls = []
    current_text_parts = []
    current_style = None

    def flush_text_parts():
        """Merge and flush the current text parts into a single Flet Text control,
        if any, and append to merged_controls.
        """
        nonlocal current_text_parts, current_style
        if current_text_parts:
            combined_text = "\n".join(current_text_parts)
            if current_style:
                color, bgcolor, weight, decoration, italic, size, text_align = current_style
                style = ft.TextStyle(
                    color=color,
                    bgcolor=bgcolor,
                    weight=weight,
                    decoration=decoration,
                    italic=italic,
                    size=size,
                )
            else:
                style = None

            merged_controls.append(ft.Text(
                combined_text,
                style=style,
                text_align=text_align if current_style and text_align else "left",
                selectable=True,
                enable_interactive_selection=True,
                expand=True,
                font_family="monospace",
            ))
            current_text_parts = []
            current_style = None

    for control in controls:
        if isinstance(control, ft.Text) and not hasattr(control, "content"):
            style = control.style or ft.TextStyle()
            style_key = (
                getattr(style, "color", None),
                getattr(style, "bgcolor", None),
                getattr(style, "weight", None),
                getattr(style, "decoration", None),
                getattr(style, "italic", None),
                getattr(style, "size", None),
                getattr(control, "text_align", None),
            )

            text_content = ""
            if hasattr(control, "spans") and control.spans:
                text_content = "".join(span.text for span in control.spans)
            elif hasattr(control, "value") and control.value:
                text_content = control.value
            else:
                text_content = ""

            if style_key == current_style:
                current_text_parts.append(text_content)
            else:
                flush_text_parts()
                current_style = style_key
                current_text_parts = [text_content]
        else:
            flush_text_parts()
            merged_controls.append(control)

    flush_text_parts()

    return ft.Container(
        content=ft.ListView(
            controls=merged_controls,
            spacing=2,
            expand=True,
        ),
        expand=True,
    )
