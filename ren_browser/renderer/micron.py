"""Micron markup renderer for Ren Browser.

Provides rendering capabilities for micron markup content,
currently implemented as a placeholder.
"""

import flet as ft


class MicronParser:
    def __init__(self, dark_theme=True, enable_force_monospace=True):
        self.dark_theme = dark_theme
        self.enable_force_monospace = enable_force_monospace
        self.DEFAULT_FG_DARK = "ddd"
        self.DEFAULT_FG_LIGHT = "222"
        self.DEFAULT_BG = "default"

        self.SELECTED_STYLES = None

        self.STYLES_DARK = {
            "plain": {"fg": self.DEFAULT_FG_DARK, "bg": self.DEFAULT_BG, "bold": False, "underline": False, "italic": False},
            "heading1": {"fg": "222", "bg": "bbb", "bold": False, "underline": False, "italic": False},
            "heading2": {"fg": "111", "bg": "999", "bold": False, "underline": False, "italic": False},
            "heading3": {"fg": "000", "bg": "777", "bold": False, "underline": False, "italic": False},
        }

        self.STYLES_LIGHT = {
            "plain": {"fg": self.DEFAULT_FG_LIGHT, "bg": self.DEFAULT_BG, "bold": False, "underline": False, "italic": False},
            "heading1": {"fg": "000", "bg": "777", "bold": False, "underline": False, "italic": False},
            "heading2": {"fg": "111", "bg": "aaa", "bold": False, "underline": False, "italic": False},
            "heading3": {"fg": "222", "bg": "ccc", "bold": False, "underline": False, "italic": False},
        }

        if self.dark_theme:
            self.SELECTED_STYLES = self.STYLES_DARK
        else:
            self.SELECTED_STYLES = self.STYLES_LIGHT

    def convert_micron_to_controls(self, markup: str) -> list[ft.Control]:
        """Convert micron markup to Flet controls."""
        controls = []
        state = self._init_state()
        lines = markup.split("\n")

        for line in lines:
            line_controls = self._parse_line(line, state)
            if line_controls:
                controls.extend(line_controls)

        return controls

    def _init_state(self) -> dict:
        """Initialize the parser state."""
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
        """Parse a single line of micron markup."""
        if not line:
            return [ft.Text("", selectable=True, font_family="monospace")]

        # Handle literal mode toggle
        if line == "`=":
            state["literal"] = not state["literal"]
            return []

        # Handle comments
        if not state["literal"] and line.startswith("#"):
            return []

        # Handle section reset
        if not state["literal"] and line.startswith("<"):
            state["depth"] = 0
            return self._parse_line(line[1:], state)

        # Handle headings
        if not state["literal"] and line.startswith(">"):
            return self._parse_heading(line, state)

        # Handle dividers
        if not state["literal"] and line.startswith("-"):
            return self._parse_divider(line, state)

        # Parse inline formatting
        return self._parse_inline_formatting(line, state)

    def _parse_inline_formatting(self, line: str, state: dict) -> list[ft.Control]:
        """Parse inline formatting within a line."""
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
            nonlocal current_text
            if current_text:
                spans.append(self._create_span(current_text, current_style))
                current_text = ""

        while i < len(line):
            if skip > 0:
                skip -= 1
                i += 1
                continue

            char = line[i]

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
                elif char == "`":
                    # End formatting, reset to plain
                    current_style["bold"] = False
                    current_style["underline"] = False
                    current_style["italic"] = False
                    current_style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
                    current_style["bg"] = self.DEFAULT_BG
                    state["align"] = state["default_align"]
                    mode = "text"
                    handled = True

                if handled:
                    i += 1
                    continue

            # Text mode
            if char == "`":
                flush_current()
                # Check for double backtick (reset)
                if i + 1 < len(line) and line[i + 1] == "`":
                    current_style["bold"] = False
                    current_style["underline"] = False
                    current_style["italic"] = False
                    current_style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
                    current_style["bg"] = self.DEFAULT_BG
                    state["align"] = state["default_align"]
                    i += 2
                    continue
                # Single backtick - enter formatting mode
                mode = "formatting"
                i += 1
                continue

            # Regular character
            current_text += char
            i += 1

        # Flush remaining text
        flush_current()

        if spans:
            return [ft.Text(spans=spans, text_align=state["align"], selectable=True, font_family="monospace")]
        return [ft.Text(line, text_align=state["align"], selectable=True, font_family="monospace")]

    def _create_span(self, text: str, style: dict) -> ft.TextSpan:
        """Create a TextSpan with the given style."""
        flet_style = ft.TextStyle(
            color=self._color_to_flet(style["fg"]),
            bgcolor=self._color_to_flet(style["bg"]),
            weight=ft.FontWeight.BOLD if style["bold"] else ft.FontWeight.NORMAL,
            decoration=ft.TextDecoration.UNDERLINE if style["underline"] else ft.TextDecoration.NONE,
            italic=style["italic"],
        )
        return ft.TextSpan(text, flet_style)

    def _apply_format_code_to_style(self, code: str, style: dict, state: dict):
        """Apply formatting code to a style dict."""
        if not code:
            return

        # Reset all formatting
        if code == "`":
            style["bold"] = False
            style["underline"] = False
            style["italic"] = False
            style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
            style["bg"] = self.DEFAULT_BG
            return

        # Toggle formatting
        if "!" in code:
            style["bold"] = not style["bold"]
        if "_" in code:
            style["underline"] = not style["underline"]
        if "*" in code:
            style["italic"] = not style["italic"]

        # Colors
        if code.startswith("F") and len(code) >= 4:
            style["fg"] = code[1:4]
        elif code.startswith("B") and len(code) >= 4:
            style["bg"] = code[1:4]

        # Reset colors
        if "f" in code:
            style["fg"] = self.SELECTED_STYLES["plain"]["fg"]
        if "b" in code:
            style["bg"] = self.DEFAULT_BG

    def _apply_format_code(self, code: str, state: dict):
        """Apply formatting code to state."""
        if not code:
            return

        # Reset all formatting
        if code == "`":
            state["formatting"]["bold"] = False
            state["formatting"]["underline"] = False
            state["formatting"]["italic"] = False
            state["fg_color"] = self.SELECTED_STYLES["plain"]["fg"]
            state["bg_color"] = self.DEFAULT_BG
            state["align"] = state["default_align"]
            return

        # Toggle formatting
        if "!" in code:
            state["formatting"]["bold"] = not state["formatting"]["bold"]
        if "_" in code:
            state["formatting"]["underline"] = not state["formatting"]["underline"]
        if "*" in code:
            state["formatting"]["italic"] = not state["formatting"]["italic"]

        # Colors
        if code.startswith("F") and len(code) >= 4:
            state["fg_color"] = code[1:4]
        elif code.startswith("B") and len(code) >= 4:
            state["bg_color"] = code[1:4]

        # Reset colors
        if "f" in code:
            state["fg_color"] = self.SELECTED_STYLES["plain"]["fg"]
        if "b" in code:
            state["bg_color"] = self.DEFAULT_BG

        # Alignment
        if "c" in code:
            state["align"] = "center"
        elif "l" in code:
            state["align"] = "left"
        elif "r" in code:
            state["align"] = "right"
        elif "a" in code:
            state["align"] = state["default_align"]

    def _parse_divider(self, line: str, state: dict) -> list[ft.Control]:
        """Parse divider lines."""
        if len(line) == 1:
            # Simple horizontal rule
            return [ft.Divider()]
        # Custom divider with repeated character
        divider_char = line[1] if len(line) > 1 else "-"
        repeated = divider_char * 80  # Fixed width for now

        divider = ft.Text(
            repeated,
            font_family="monospace",
            color=self._color_to_flet(state["fg_color"]),
            bgcolor=self._color_to_flet(state["bg_color"]),
            no_wrap=True,
            overflow=ft.TextOverflow.CLIP,
            selectable=False,  # Dividers don't need to be selectable
        )

        return [divider]

    def _color_to_flet(self, color: str) -> str | None:
        """Convert micron color format to Flet color format."""
        if not color or color == "default":
            return None

        # 3-char hex (like "ddd")
        if len(color) == 3 and all(c in "0123456789abcdefABCDEF" for c in color):
            return f"#{color[0]*2}{color[1]*2}{color[2]*2}"

        # 6-char hex
        if len(color) == 6 and all(c in "0123456789abcdefABCDEF" for c in color):
            return f"#{color}"

        # Grayscale format "gXX"
        if len(color) == 3 and color[0] == "g":
            try:
                val = int(color[1:])
                if 0 <= val <= 99:
                    h = hex(int(val * 2.55))[2:].zfill(2)
                    return f"#{h}{h}{h}"
            except ValueError:
                pass

        return None

    def _parse_heading(self, line: str, state: dict) -> list[ft.Control]:
        """Parse heading lines."""
        # Count the number of > characters
        heading_level = 0
        for char in line:
            if char == ">":
                heading_level += 1
            else:
                break

        heading_text = line[heading_level:].strip()

        if heading_text:
            # Apply heading style
            style_key = f"heading{min(heading_level, 3)}"
            style = self.SELECTED_STYLES.get(style_key, self.SELECTED_STYLES["plain"])

            # Create heading control
            heading = ft.Text(
                heading_text,
                style=ft.TextStyle(
                    color=self._color_to_flet(style["fg"]),
                    bgcolor=self._color_to_flet(style["bg"]),
                    weight=ft.FontWeight.BOLD if style["bold"] else ft.FontWeight.NORMAL,
                    size=20 - heading_level * 2,  # Smaller size for deeper headings
                ),
                selectable=True,
                font_family="monospace",
            )

            return [heading]

        return []


def render_micron(content: str) -> ft.Control:
    """Render micron markup content to a Flet control.

    Args:
        content: Micron markup content to render.

    Returns:
        ft.Control: Rendered content as a Flet control.

    """
    parser = MicronParser()
    controls = parser.convert_micron_to_controls(content)
    return ft.Column(
        controls=controls,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=2,  # Small spacing between lines for readability
    )
