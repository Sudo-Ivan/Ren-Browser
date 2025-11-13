from ren_browser.pages.page_request import PageRequest


class TestPageRequest:
    """Test cases for the PageRequest dataclass."""

    def test_page_request_creation(self):
        """Test basic PageRequest creation."""
        request = PageRequest(
            destination_hash="1234567890abcdef", page_path="/page/index.mu",
        )

        assert request.destination_hash == "1234567890abcdef"
        assert request.page_path == "/page/index.mu"
        assert request.field_data is None

    def test_page_request_with_field_data(self):
        """Test PageRequest creation with field data."""
        field_data = {"key": "value", "form_field": "data"}
        request = PageRequest(
            destination_hash="1234567890abcdef",
            page_path="/page/form.mu",
            field_data=field_data,
        )

        assert request.destination_hash == "1234567890abcdef"
        assert request.page_path == "/page/form.mu"
        assert request.field_data == field_data

    def test_page_request_validation(self):
        """Test PageRequest field validation."""
        # Test with various path formats
        request1 = PageRequest("hash1", "/")
        request2 = PageRequest("hash2", "/page/test.mu")
        request3 = PageRequest("hash3", "/deep/nested/path/file.mu")

        assert request1.page_path == "/"
        assert request2.page_path == "/page/test.mu"
        assert request3.page_path == "/deep/nested/path/file.mu"

        # Test with different hash formats
        assert request1.destination_hash == "hash1"
        assert len(request1.destination_hash) > 0


# NOTE: PageFetcher tests are complex due to RNS networking integration.
# These will be implemented when the networking layer is more stable.
class TestPageFetcher:
    """Test cases for the PageFetcher class.

    Note: These tests are simplified due to complex RNS networking integration.
    Full integration tests will be added when the networking layer is stable.
    """

    def test_page_fetcher_concepts(self):
        """Test basic concepts that PageFetcher should handle."""
        # Test that we can create PageRequest objects for the fetcher
        requests = [
            PageRequest("hash1", "/index.mu"),
            PageRequest("hash2", "/about.mu", {"form": "data"}),
            PageRequest("hash3", "/contact.mu"),
        ]

        # Test that requests have the expected structure
        assert all(hasattr(req, "destination_hash") for req in requests)
        assert all(hasattr(req, "page_path") for req in requests)
        assert all(hasattr(req, "field_data") for req in requests)

        # Test request with form data
        form_request = requests[1]
        assert form_request.field_data == {"form": "data"}

        # Test requests without form data
        simple_requests = [req for req in requests if req.field_data is None]
        assert len(simple_requests) == 2
