from ren_browser.announces.announces import Announce


class TestAnnounce:
    """Test cases for the Announce dataclass."""

    def test_announce_creation(self):
        """Test basic Announce creation."""
        announce = Announce(
            destination_hash="1234567890abcdef",
            display_name="Test Node",
            timestamp=1234567890,
        )

        assert announce.destination_hash == "1234567890abcdef"
        assert announce.display_name == "Test Node"
        assert announce.timestamp == 1234567890

    def test_announce_with_none_display_name(self):
        """Test Announce creation with None display name."""
        announce = Announce(
            destination_hash="1234567890abcdef", display_name=None, timestamp=1234567890
        )

        assert announce.destination_hash == "1234567890abcdef"
        assert announce.display_name is None
        assert announce.timestamp == 1234567890


class TestAnnounceService:
    """Test cases for the AnnounceService class.

    Note: These tests are simplified due to complex RNS integration.
    Full integration tests will be added in the future.
    """

    def test_announce_dataclass_functionality(self):
        """Test that the Announce dataclass works correctly."""
        # Test that we can create and use Announce objects
        announce1 = Announce("hash1", "Node1", 1000)
        announce2 = Announce("hash2", None, 2000)

        # Test that announces can be stored in lists
        announces = [announce1, announce2]
        assert len(announces) == 2
        assert announces[0].display_name == "Node1"
        assert announces[1].display_name is None

        # Test that we can filter announces by hash
        filtered = [ann for ann in announces if ann.destination_hash == "hash1"]
        assert len(filtered) == 1
        assert filtered[0].display_name == "Node1"
