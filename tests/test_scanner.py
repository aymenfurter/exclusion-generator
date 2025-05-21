import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch
import gradio as gr
from ghcp_exclusion_builder.scanner import scan_directory_for_pii


@pytest.fixture
def mock_analyzer():
    """Fixture to mock the presidio analyzer."""
    with patch('ghcp_exclusion_builder.scanner.get_presidio_analyzer') as mock_get_analyzer:
        mock_analyzer = MagicMock()
        mock_get_analyzer.return_value = mock_analyzer
        yield mock_analyzer


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory with test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create some test files
        test_files = {
            'file1.txt': 'This is a test file with no PII.',
            'file2.txt': 'This file contains John Doe as a name.',
            'subdir/file3.txt': 'Another file with Jane Smith in it.',
            'excluded.pyc': 'This should be excluded based on extension.',
            'node_modules/library.js': 'This should be excluded based on directory.'
        }
        
        for file_path, content in test_files.items():
            full_path = os.path.join(tmp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
                
        yield tmp_dir


def test_scan_directory_basic(temp_test_dir, mock_analyzer):
    """Test basic scanning functionality."""
    # Configure mock analyzer to return no results
    mock_analyzer.analyze.return_value = []
    
    # Run scan with default settings and no exclusions
    progress_mock = MagicMock(spec=gr.Progress)
    result = scan_directory_for_pii(
        temp_test_dir,
        selected_presets=None,
        custom_exclusions_str="",
        progress=progress_mock
    )
    
    # Check that the result is a string (output text)
    assert isinstance(result, str)
    # Verify scan completed message is in result
    assert "Scan complete" in result
    # Check that we called analyze at least once
    assert mock_analyzer.analyze.called


def test_scan_directory_with_exclusions(temp_test_dir, mock_analyzer):
    """Test scanning with exclusion patterns."""
    # Configure mock analyzer to return no results
    mock_analyzer.analyze.return_value = []
    
    # Create a pyc file that should be excluded by default
    with open(os.path.join(temp_test_dir, 'excluded.pyc'), 'w') as f:
        f.write('This should be excluded based on extension.')
    
    # Run scan with custom exclusions for text files
    progress_mock = MagicMock(spec=gr.Progress)
    result = scan_directory_for_pii(
        temp_test_dir,
        selected_presets=None,
        custom_exclusions_str="*.txt",  # Exclude all txt files
        progress=progress_mock
    )
    
    # The scan should complete with no PII found
    assert "Scan complete" in result
    assert "No significant PII found" in result


def test_scan_directory_with_presets(temp_test_dir, mock_analyzer):
    """Test scanning with preset exclusions."""
    # Configure mock analyzer to return no results
    mock_analyzer.analyze.return_value = []
    
    # Run scan with Node.js preset (should exclude node_modules)
    progress_mock = MagicMock(spec=gr.Progress)
    result = scan_directory_for_pii(
        temp_test_dir,
        selected_presets=["Node.js"],
        custom_exclusions_str="",
        progress=progress_mock
    )
    
    # The scan should complete, and node_modules files should be excluded
    assert "Scan complete" in result
    
    # Check if node_modules wasn't scanned by checking analyze calls
    for call_args in mock_analyzer.analyze.call_args_list:
        # The first arg would be the text content
        content = call_args[1]['text']
        assert "library.js" not in content  # From node_modules
