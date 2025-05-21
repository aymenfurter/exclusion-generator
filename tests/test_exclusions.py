import pytest
from ghcp_exclusion_builder.exclusions import is_excluded

# Test cases for is_excluded function
# Each tuple: (item_path, patterns, expected_result, description)
EXCLUSION_TEST_CASES = [
    # Basic directory exclusion
    ("foo/bar.txt", ["foo/**"], True, "Direct sub-file of excluded dir"),
    ("foo/baz/bar.txt", ["foo/**"], True, "Nested sub-file of excluded dir"),
    ("foo/", ["foo/**"], True, "Excluded directory itself"),
    ("other/foo/bar.txt", ["foo/**"], True,
     "Sub-file of dir matching relative pattern"),
    ("bar.txt", ["foo/**"], False, "File not in excluded dir"),

    # Absolute directory exclusion (from scan root)
    ("foo/bar.txt", ["/foo/**"], True,
     "Direct sub-file of absolute excluded dir"),
    ("foo/", ["/foo/**"], True, "Absolute excluded directory itself"),
    ("other/foo/bar.txt", ["/foo/**"], False,
     "File not in absolute excluded dir (nested)"),

    # Glob pattern exclusion (basename)
    ("foo/bar.txt", ["*.txt"], True, "Txt file matching glob"),
    ("foo/bar.log", ["*.txt"], False, "Log file not matching txt glob"),
    ("image.jpg", ["*.jpg"], True, "Jpg file matching glob"),

    # Glob pattern exclusion (path)
    ("src/foo/bar.py", ["src/**/*.py"], True,
     "Python file in src matching path glob"),
    ("tests/foo/bar.py", ["src/**/*.py"], False,
     "Python file not in src for path glob"),
    ("a/b/c/file.tmp", ["**/b/**/*.tmp"], True,
     "Temp file matching complex path glob"),

    # Exact file exclusion (basename)
    ("foo/LICENSE", ["LICENSE"], True, "LICENSE file in subdir"),
    ("LICENSE", ["LICENSE"], True, "LICENSE file in root"),
    ("foo/README.md", ["LICENSE"], False, "README not matching LICENSE"),

    # Exact file exclusion (relative path)
    ("docs/README.md", ["docs/README.md"], True,
     "Exact relative path match"),
    ("README.md", ["docs/README.md"], False,
     "Root README not matching relative path"),

    # Exact file exclusion (absolute path from scan root)
    ("config/settings.ini", ["/config/settings.ini"], True,
     "Exact absolute path match"),
    ("settings.ini", ["/config/settings.ini"], False,
     "Root file not matching absolute path"),

    # Mixed and multiple patterns
    ("node_modules/lib/file.js", ["/node_modules/**", "*.log"], True,
     "JS file in node_modules"),
    ("app.log", ["/node_modules/**", "*.log"], True,
     "Log file matching glob"),
    ("src/main.py", ["/node_modules/**", "*.log"], False,
     "Python file not matching any"),

    # Patterns with leading/trailing spaces
    ("foo/bar.txt", ["  foo/**  "], True,
     "Pattern with spaces around dir exclusion"),
    ("bar.txt", ["  *.txt  "], True,
     "Pattern with spaces around glob"),

    # Empty or invalid patterns
    ("foo/bar.txt", [""], False, "Empty pattern string"),
    ("foo/bar.txt", ["  "], False, "Whitespace-only pattern string"),
    ("foo/bar.txt", ["", "*.txt"], True,
     "Empty pattern with a valid one"),

    # Directory path normalization for pruning check (path ends with /)
    ("foo/bar/", ["foo/bar/**"], True,
     "Directory path for pruning (ends with /)"),
    ("foo/bar/", ["/foo/bar/**"], True,
     "Absolute directory path for pruning"),
    ("foo/", ["foo/**"], True, "Top-level directory for pruning"),

    # Edge cases
    (".git/config", ["/.git/**"], True, "Git config file"),
    ("file.pyc", ["*.pyc"], True, "Pyc file"),
    ("project/build/output.o", ["/build/**"], False,
     "Build output not at root build dir"),
    ("project/build/output.o", ["build/**"], True,
     "Build output in relative build dir"),
]


@pytest.mark.parametrize(
    "item_path, patterns, expected, description",
    EXCLUSION_TEST_CASES
)
def test_is_excluded(item_path, patterns, expected, description):
    assert is_excluded(item_path, patterns) == expected, description
