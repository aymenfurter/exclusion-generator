import pytest
from ghcp_exclusion_builder.exclusions import EXCLUSION_PRESETS, is_excluded

# Test cases for exclusion presets
# Each tuple: (preset_name, test_file_path, expected_result, description)
PRESET_TEST_CASES = [
    # Generic preset tests
    ("Generic", ".git/config", True, "Git directory should be excluded in Generic preset"),
    ("Generic", "README.md", True, "README.md should be excluded in Generic preset"),
    ("Generic", "LICENSE", True, "LICENSE should be excluded in Generic preset"),
    ("Generic", "src/main.py", False, "Python file should not be excluded in Generic preset"),
    
    # Python preset tests
    ("Python", "__pycache__/cache.pyc", True, "Python cache dir should be excluded in Python preset"),
    ("Python", "file.pyc", True, "Pyc file should be excluded in Python preset"),
    ("Python", ".venv/lib/site-packages/lib.py", True, "Venv dir should be excluded in Python preset"),
    ("Python", "src/main.py", False, "Python source file should not be excluded in Python preset"),
    
    # Java preset tests
    ("Java", "target/app.jar", True, "Target dir should be excluded in Java preset"),
    ("Java", "build/classes/main/App.class", True, "Build dir should be excluded in Java preset"),
    ("Java", ".gradle/cache.properties", True, "Gradle dir should be excluded in Java preset"),
    ("Java", "src/main/java/App.java", False, "Java source file should not be excluded in Java preset"),
    
    # C# preset tests
    ("C#", "bin/Debug/app.exe", True, "Bin dir should be excluded in C# preset"),
    ("C#", "obj/Debug/app.pdb", True, "Obj dir should be excluded in C# preset"),
    ("C#", "project.csproj", True, "Csproj file should be excluded in C# preset"),
    ("C#", "src/App.cs", False, "C# source file should not be excluded in C# preset"),
    
    # Node.js preset tests
    ("Node.js", "node_modules/express/index.js", True, "Node modules should be excluded in Node.js preset"),
    ("Node.js", "package-lock.json", True, "Package lock should be excluded in Node.js preset"),
    ("Node.js", "yarn.lock", True, "Yarn lock should be excluded in Node.js preset"),
    ("Node.js", "src/index.js", False, "JS source file should not be excluded in Node.js preset"),
]


@pytest.mark.parametrize(
    "preset_name, file_path, expected, description",
    PRESET_TEST_CASES
)
def test_exclusion_presets(preset_name, file_path, expected, description):
    """Test that preset exclusion patterns work correctly."""
    preset_patterns = EXCLUSION_PRESETS.get(preset_name, [])
    assert preset_patterns, f"Preset {preset_name} should exist"
    
    # Test if the file would be excluded using patterns from this preset
    result = is_excluded(file_path, preset_patterns)
    assert result == expected, description


def test_preset_comprehensiveness():
    """Test that all expected presets exist."""
    expected_presets = ["Generic", "Python", "Java", "C#", "Node.js"]
    for preset in expected_presets:
        assert preset in EXCLUSION_PRESETS, f"Expected preset {preset} to exist"
        assert len(EXCLUSION_PRESETS[preset]) > 0, f"Preset {preset} should have patterns"
