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
    
    Note: The micron renderer is currently a placeholder implementation
    that displays raw content without markup processing.
    """

    def test_render_micron_basic(self):
        """Test basic micron rendering (currently displays raw content)."""
        content = "# Heading\n\nSome content"
        result = render_micron(content)

        assert isinstance(result, ft.Text)
        assert result.value == "# Heading\n\nSome content"
        assert result.selectable is True
        assert result.font_family == "monospace"
        assert result.expand is True

    def test_render_micron_empty(self):
        """Test micron rendering with empty content."""
        content = ""
        result = render_micron(content)

        assert isinstance(result, ft.Text)
        assert result.value == ""
        assert result.selectable is True

    def test_render_micron_unicode(self):
        """Test micron rendering with Unicode characters."""
        content = "Unicode content: 你好 🌍 αβγ"
        result = render_micron(content)

        assert isinstance(result, ft.Text)
        assert result.value == content
        assert result.selectable is True


class TestRendererComparison:
    """Test cases comparing both renderers."""

    def test_renderers_return_same_type(self):
        """Test that both renderers return the same control type."""
        content = "Test content"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        assert type(plaintext_result) is type(micron_result)
        assert isinstance(plaintext_result, ft.Text)
        assert isinstance(micron_result, ft.Text)

    def test_renderers_preserve_content(self):
        """Test that both renderers preserve the original content."""
        content = "Test content with\nmultiple lines"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        assert plaintext_result.value == content
        assert micron_result.value == content

    def test_renderers_same_properties(self):
        """Test that both renderers set the same basic properties."""
        content = "Test content"

        plaintext_result = render_plaintext(content)
        micron_result = render_micron(content)

        assert plaintext_result.selectable == micron_result.selectable
        assert plaintext_result.font_family == micron_result.font_family
        assert plaintext_result.expand == micron_result.expand
