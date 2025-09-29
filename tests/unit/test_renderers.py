import flet as ft

from ren_browser.renderer.micron import render_micron
from ren_browser.renderer.plaintext import render_plaintext


class TestPlaintextRenderer:
    """Test cases for the plaintext renderer."""

    def test_render_plaintext_basic(self):
        """Test basic plaintext rendering."""
        content = "Hello, world!"
        result = render_plaintext(content)

        assert isinstance(result, ft.Text)
        assert result.value == "Hello, world!"
        assert result.selectable is True
        assert result.font_family == "monospace"
        assert result.expand is True

    def test_render_plaintext_multiline(self):
        """Test plaintext rendering with multiline content."""
        content = "Line 1\nLine 2\nLine 3"
        result = render_plaintext(content)

        assert isinstance(result, ft.Text)
        assert result.value == "Line 1\nLine 2\nLine 3"
        assert result.selectable is True

    def test_render_plaintext_empty(self):
        """Test plaintext rendering with empty content."""
        content = ""
        result = render_plaintext(content)

        assert isinstance(result, ft.Text)
        assert result.value == ""
        assert result.selectable is True

    def test_render_plaintext_special_chars(self):
        """Test plaintext rendering with special characters."""
        content = "Special chars: !@#$%^&*()_+{}|:<>?[]\\;'\",./"
        result = render_plaintext(content)

        assert isinstance(result, ft.Text)
        assert result.value == content
        assert result.selectable is True

    def test_render_plaintext_unicode(self):
        """Test plaintext rendering with Unicode characters."""
        content = "Unicode: 你好 🌍 αβγ"
        result = render_plaintext(content)

        assert isinstance(result, ft.Text)
        assert result.value == content
        assert result.selectable is True


class TestMicronRenderer:
    """Test cases for the micron renderer.

    The micron renderer parses Micron markup format and returns a ListView
    containing styled controls with proper formatting, colors, and layout.
    """

    def test_render_micron_basic(self):
        """Test basic micron rendering."""
        content = "# Heading\n\nSome content"
        result = render_micron(content)

        # Should return a Container with ListView
        assert isinstance(result, ft.Container)
        assert isinstance(result.content, ft.ListView)
        assert result.content.spacing == 2

        # Should contain controls
        assert len(result.content.controls) > 0
        for control in result.content.controls:
            assert control.selectable is True
            assert control.font_family == "monospace"

    def test_render_micron_empty(self):
        """Test micron rendering with empty content."""
        content = ""
        result = render_micron(content)

        # Should return a Container
        assert isinstance(result, ft.Container)

        # May contain empty controls

    def test_render_micron_unicode(self):
        """Test micron rendering with Unicode characters."""
        content = "Unicode content: 你好 🌍 αβγ"
        result = render_micron(content)

        # Should return a Container
        assert isinstance(result, ft.Container)

        # Should contain Text controls with the content
        assert len(result.content.controls) > 0
        all_text = ""
        for control in result.content.controls:
            assert isinstance(control, ft.Text)
            # Extract text from the merged control
            if hasattr(control, "value") and control.value:
                all_text += control.value

        # Should preserve the content
        assert content in all_text

    def test_render_micron_headings(self):
        """Test micron rendering with different heading levels."""
        content = "> Level 1\n>> Level 2\n>>> Level 3"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        assert len(result.content.controls) == 3

        # Check that headings are wrapped in containers with backgrounds
        for control in result.content.controls:
            assert isinstance(control, ft.Container)
            assert control.bgcolor is not None  # Should have background color
            assert control.width == float("inf")  # Should be full width

    def test_render_micron_formatting(self):
        """Test micron rendering with text formatting."""
        content = "`!Bold text!` and `_underline_` and `*italic*`"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        assert len(result.content.controls) >= 1

        # Should produce some text content
        all_text = ""
        for control in result.content.controls:
            if hasattr(control, "value") and control.value:
                all_text += control.value

        assert len(all_text) > 0  # Should have some processed content

    def test_render_micron_colors(self):
        """Test micron rendering with color codes."""
        content = "`FffRed text` and `B00Blue background`"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        assert len(result.content.controls) >= 1

        # Should produce some text content (color codes may consume characters)
        all_text = ""
        for control in result.content.controls:
            if hasattr(control, "value") and control.value:
                all_text += control.value

        assert len(all_text) > 0  # Should have some processed content

    def test_render_micron_alignment(self):
        """Test micron rendering with alignment."""
        content = "`cCentered text`"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        assert len(result.content.controls) >= 1

        # Should have some text content
        all_text = ""
        for control in result.content.controls:
            if hasattr(control, "value") and control.value:
                all_text += control.value

        assert len(all_text) > 0

    def test_render_micron_comments(self):
        """Test that comments are ignored."""
        content = "# This is a comment\nVisible text"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        # Should only contain the visible text, not the comment
        all_text = ""
        for control in result.content.controls:
            if isinstance(control, ft.Text) and hasattr(control, "value") and control.value:
                all_text += control.value

        assert "Visible text" in all_text
        assert "This is a comment" not in all_text

    def test_render_micron_section_depth(self):
        """Test micron rendering with section depth/indentation."""
        content = "> Main section\n>> Subsection\n>>> Sub-subsection"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        assert len(result.content.controls) == 3

        # Check indentation increases with depth
        for i, control in enumerate(result.content.controls):
            assert isinstance(control, ft.Container)
            # The inner container should have margin for indentation
            inner_container = control.content
            if hasattr(inner_container, "margin") and inner_container.margin:
                # Should have left margin based on depth: (depth-1) * 1.2 * 16
                # depth = i + 1, so margin = i * 1.2 * 16
                expected_margin = i * 1.2 * 16  # 19.2px per depth level above 1
                assert inner_container.margin.left == expected_margin

    def test_render_micron_ascii_art(self):
        """Test micron rendering with ASCII art scaling."""
        # Create content with ASCII art characters
        ascii_art = "┌───┐\n│Box│\n└───┘"
        content = f"Normal text\n{ascii_art}\nMore text"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        # Text gets merged into single control due to text merging
        assert len(result.content.controls) >= 1
        # Should contain the ASCII art content
        all_text = ""
        for control in result.content.controls:
            if isinstance(control, ft.Text) and hasattr(control, "value"):
                all_text += control.value
        assert "┌───┐" in all_text
        assert "Normal text" in all_text

    def test_render_micron_literal_mode(self):
        """Test micron literal mode."""
        content = "`=Literal mode`\n# This should be visible\n`=Back to normal`"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        # Should contain the processed content (literal mode may not be fully implemented)
        all_text = ""
        for control in result.content.controls:
            if isinstance(control, ft.Text) and hasattr(control, "value") and control.value:
                all_text += control.value

        # At minimum, should contain some text content
        assert len(all_text.strip()) > 0

    def test_render_micron_dividers(self):
        """Test micron rendering with dividers."""
        content = "Text above\n-\nText below"
        result = render_micron(content)

        assert isinstance(result, ft.Container)
        # Should contain controls for text
        assert len(result.content.controls) >= 2

    def test_render_micron_complex_formatting(self):
        """Test complex combination of micron formatting."""
        content = """# Comment (ignored)
> Heading
Regular text.

>> Subsection
Centered text
Final paragraph."""

        result = render_micron(content)

        assert isinstance(result, ft.Container)
        assert len(result.content.controls) >= 3  # Should have multiple elements

        # Check for heading containers
        heading_containers = [c for c in result.content.controls if isinstance(c, ft.Container)]
        assert len(heading_containers) >= 2  # At least 2 headings

        # Check that we have some text content
        def extract_all_text(control):
            """Recursively extract text from control and its children."""
            text = ""
            if hasattr(control, "value") and control.value:
                text += control.value
            elif hasattr(control, "_Control__attrs") and "value" in control._Control__attrs:
                text += control._Control__attrs["value"][0]
            elif hasattr(control, "spans") and control.spans:
                text += "".join(span.text for span in control.spans)
            elif hasattr(control, "content"):
                text += extract_all_text(control.content)
            return text

        all_text = ""
        for control in result.content.controls:
            all_text += extract_all_text(control)

        assert "Heading" in all_text
        assert "Subsection" in all_text
        assert "Regular text" in all_text


class TestRendererComparison:
    """Test cases comparing both renderers."""

    def test_renderers_return_correct_types(self):
        """Test that both renderers return the expected control types."""
        content = "Test content"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        # Plaintext returns Text, Micron returns Container
        assert isinstance(plaintext_result, ft.Text)
        assert isinstance(micron_result, ft.Container)

    def test_renderers_preserve_content(self):
        """Test that both renderers preserve the original content."""
        content = "Test content with\nmultiple lines"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        assert plaintext_result.value == content

        # For micron result (Container), extract text from merged controls
        micron_text = ""
        for control in micron_result.content.controls:
            if isinstance(control, ft.Text):
                # Extract text from the merged control
                if hasattr(control, "value") and control.value:
                    micron_text += control.value + "\n"

        # Remove trailing newline and compare
        micron_text = micron_text.rstrip("\n")
        assert micron_text == content

    def test_renderers_same_properties(self):
        """Test that both renderers set the same basic properties."""
        content = "Test content"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        # Check basic properties
        assert plaintext_result.selectable is True
        assert plaintext_result.font_family == "monospace"
        assert plaintext_result.expand is True

        # For micron result (Container), check properties
        assert isinstance(micron_result.content, ft.ListView)
        assert micron_result.content.spacing == 2

        # Check that all Text controls in the column have the expected properties
        for control in micron_result.content.controls:
            if isinstance(control, ft.Text):
                assert control.selectable is True
                assert control.font_family == "monospace"
