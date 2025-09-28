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

        # Should return a ListView containing controls
        assert isinstance(result, ft.ListView)
        assert result.expand is True
        assert result.spacing == 2

        # Should contain controls
        assert len(result.controls) > 0
        for control in result.controls:
            assert control.selectable is True
            assert control.font_family == "monospace"

    def test_render_micron_empty(self):
        """Test micron rendering with empty content."""
        content = ""
        result = render_micron(content)

        # Should return a ListView
        assert isinstance(result, ft.ListView)
        assert result.expand is True

        # May contain empty controls

    def test_render_micron_unicode(self):
        """Test micron rendering with Unicode characters."""
        content = "Unicode content: 你好 🌍 αβγ"
        result = render_micron(content)

        # Should return a ListView
        assert isinstance(result, ft.ListView)
        assert result.expand is True

        # Should contain Text controls with the content
        assert len(result.controls) > 0
        all_text = ""
        for control in result.controls:
            assert isinstance(control, ft.Text)
            # Extract text from the merged control
            if hasattr(control, "_Control__attrs") and "value" in control._Control__attrs:
                all_text += control._Control__attrs["value"][0]

        # Should preserve the content
        assert content in all_text


class TestRendererComparison:
    """Test cases comparing both renderers."""

    def test_renderers_return_correct_types(self):
        """Test that both renderers return the expected control types."""
        content = "Test content"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        # Plaintext returns Text, Micron returns ListView
        assert isinstance(plaintext_result, ft.Text)
        assert isinstance(micron_result, ft.ListView)

    def test_renderers_preserve_content(self):
        """Test that both renderers preserve the original content."""
        content = "Test content with\nmultiple lines"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        assert plaintext_result.value == content

        # For micron result (ListView), extract text from merged controls
        micron_text = ""
        for control in micron_result.controls:
            if isinstance(control, ft.Text):
                # Extract text from the merged control
                if hasattr(control, "_Control__attrs") and "value" in control._Control__attrs:
                    micron_text += control._Control__attrs["value"][0] + "\n"

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

        # For micron result (ListView), check properties
        assert micron_result.expand is True
        assert micron_result.spacing == 2

        # Check that all Text controls in the column have the expected properties
        for control in micron_result.controls:
            if isinstance(control, ft.Text):
                assert control.selectable is True
                assert control.font_family == "monospace"
