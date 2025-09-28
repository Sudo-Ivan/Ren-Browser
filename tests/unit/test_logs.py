import datetime
from unittest.mock import Mock, patch

from ren_browser import logs


class TestLogsModule:
    """Test cases for the logs module."""

    def setup_method(self):
        """Reset logs before each test."""
        logs.APP_LOGS.clear()
        logs.ERROR_LOGS.clear()
        logs.RET_LOGS.clear()

    def test_initial_state(self):
        """Test that logs start empty."""
        assert logs.APP_LOGS == []
        assert logs.ERROR_LOGS == []
        assert logs.RET_LOGS == []

    def test_log_error(self):
        """Test log_error function."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now

            logs.log_error("Test error message")

            assert len(logs.ERROR_LOGS) == 1
            assert len(logs.APP_LOGS) == 1
            assert logs.ERROR_LOGS[0] == "[2023-01-01T12:00:00] Test error message"
            assert logs.APP_LOGS[0] == "[2023-01-01T12:00:00] ERROR: Test error message"

    def test_log_app(self):
        """Test log_app function."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now

            logs.log_app("Test app message")

            assert len(logs.APP_LOGS) == 1
            assert logs.APP_LOGS[0] == "[2023-01-01T12:00:00] Test app message"

    def test_log_ret_with_original_function(self, mock_rns):
        """Test log_ret function calls original RNS.log."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now

            logs._original_rns_log = Mock(return_value="original_result")

            result = logs.log_ret("Test RNS message", "arg1", kwarg1="value1")

            assert len(logs.RET_LOGS) == 1
            assert logs.RET_LOGS[0] == "[2023-01-01T12:00:00] Test RNS message"
            logs._original_rns_log.assert_called_once_with(
                "Test RNS message", "arg1", kwarg1="value1",
            )
            assert result == "original_result"

    def test_multiple_log_calls(self):
        """Test multiple log calls accumulate correctly."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now

            logs.log_error("Error 1")
            logs.log_error("Error 2")
            logs.log_app("App message")

            assert len(logs.ERROR_LOGS) == 2
            assert len(logs.APP_LOGS) == 3  # 2 errors + 1 app message
            assert logs.ERROR_LOGS[0] == "[2023-01-01T12:00:00] Error 1"
            assert logs.ERROR_LOGS[1] == "[2023-01-01T12:00:00] Error 2"
            assert logs.APP_LOGS[2] == "[2023-01-01T12:00:00] App message"

    def test_timestamp_format(self):
        """Test that timestamps are properly formatted."""
        real_datetime = datetime.datetime(2023, 1, 1, 12, 30, 45, 123456)

        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = real_datetime

            logs.log_app("Test message")

            expected_timestamp = real_datetime.isoformat()
            assert logs.APP_LOGS[0] == f"[{expected_timestamp}] Test message"

    def test_rns_log_replacement(self, mock_rns):
        """Test that RNS.log replacement concept works."""
        import ren_browser.logs as logs_module

        # Test that the log_ret function exists and is callable
        assert hasattr(logs_module, "log_ret")
        assert callable(logs_module.log_ret)

        # Test that we can call the log function
        logs_module.log_ret("test message")

        # Verify that RET_LOGS was updated
        assert len(logs_module.RET_LOGS) > 0

    def test_original_rns_log_stored(self, mock_rns):
        """Test that original RNS.log function is stored."""
        original_log = Mock()

        with patch.object(logs, "_original_rns_log", original_log):
            logs.log_ret("test message")
            original_log.assert_called_once_with("test message")

    def test_empty_message_handling(self):
        """Test handling of empty messages."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now

            logs.log_error("")
            logs.log_app("")

            assert logs.ERROR_LOGS[0] == "[2023-01-01T12:00:00] "
            assert logs.APP_LOGS[0] == "[2023-01-01T12:00:00] ERROR: "
            assert logs.APP_LOGS[1] == "[2023-01-01T12:00:00] "

    def test_special_characters_in_messages(self):
        """Test handling of special characters in log messages."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = Mock()
            mock_now.isoformat.return_value = "2023-01-01T12:00:00"
            mock_datetime.now.return_value = mock_now

            special_msg = "Message with\nnewlines\tand\ttabs and unicode: 🚀"
            logs.log_app(special_msg)

            assert logs.APP_LOGS[0] == f"[2023-01-01T12:00:00] {special_msg}"
