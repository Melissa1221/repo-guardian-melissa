"""Unit tests for command completion functionality."""

from unittest.mock import MagicMock, Mock, patch


def test_argcomplete_integration():
    """Test that argcomplete is properly integrated with the CLI."""
    # Import the CLI module directly
    import guardian.cli

    # Create a copy of the original import function
    original_import = __import__

    # Create mock argcomplete module
    mock_argcomplete = Mock()

    # Mock the import function to return our mock when importing argcomplete
    def mock_import(name, *args, **kwargs):
        if name == "argcomplete":
            return mock_argcomplete
        return original_import(name, *args, **kwargs)

    # Patch __import__ temporarily
    with patch("builtins.__import__", side_effect=mock_import):
        # Create a mock parser
        mock_parser = Mock()
        with patch("argparse.ArgumentParser", return_value=mock_parser):
            # Call the main function which should use argcomplete
            guardian.cli.main()

            # Verify argcomplete was used
            mock_argcomplete.autocomplete.assert_called_once_with(mock_parser)


@patch("guardian.cli.argcomplete", create=True)
def test_argcomplete_import_error(mock_argcomplete):
    """Test that ImportError for argcomplete is handled gracefully."""
    # Configure mock to raise ImportError when used
    mock_argcomplete.autocomplete.side_effect = ImportError()

    # Import the module that should handle ImportError
    from guardian.cli import main

    with patch("guardian.cli.argparse.ArgumentParser") as mock_parser_cls:
        parser = mock_parser_cls.return_value
        parser.add_subparsers.return_value = MagicMock()
        parser.parse_args.return_value.command = None

        # This should not raise an exception
        main()

        # Verify parser was created
        mock_parser_cls.assert_called_once()
