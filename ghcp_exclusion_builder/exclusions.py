import os
import fnmatch

# --- Configuration ---
COMMON_NON_TEXT_EXCLUSIONS = [
    # Common VCS directories
    "/.git/**",
    # Images
    "*.dicom", "*.DICOM", "*.npy", "*.DCM*", "*.dcm", "*.bmp", "*.gif", "*.ico", "*.jpeg", "*.jpg", "*.png",
    "*.tiff", "*.webp",
    # Documents (often binary or complex structure)
    # Not ideal for plain text PII scan
    "*.doc", "*.docx", "*.pdf", "*.ppt", "*.pptx", "*.xls", "*.xlsx",
    # Archives
    "*.7z", "*.bz2", "*.gz", "*.rar", "*.tar", "*.xz", "*.zip",
    # Executables & Libraries
    "*.a", "*.app", "*.dll", "*.dylib", "*.exe", "*.lib", "*.msi", "*.o",
    "*.so",
    # Compiled code / Intermediates (already in Python preset, but good to have
    # generally)
    "*.class", "*.pyc", "*.pyo",
    # Audio/Video
    "*.aac", "*.avi", "*.mkv", "*.mov", "*.mp3", "*.mp4", "*.ogg",
    "*.wav", "*.webm",
    # Fonts
    "*.eot", "*.otf", "*.ttf", "*.woff", "*.woff2",
    # Other common non-text or build artifacts
    "*.DS_Store",
    "*.db",
    # e.g. package-lock.json, yarn.lock - often large and not primary PII
    # source
    "*.lock",
    # Logs can be noisy, added here for broad non-text
    "*.log",
    "*.sqlite",
    # Vim swap files
    "*.swo",
    "*.swp",
]

EXCLUSION_PRESETS = {
    "Python": [
        "*.pyc",
        "/__pycache__/**",
        "/.venv/**",
        "/.env",
        "/.pytest_cache/**",
        "/build/**",
        "/dist/**",
        "*.egg-info/**",
        "setup.py",
        "requirements.txt",
    ],
    "Java": [
        "*.class",
        "/target/**",
        "/.gradle/**",
        "/build/**",
        "*.jar",
        "*.war",
        "*.ear",
        ".settings/**",
        "*.classpath",
        "*.project",
    ],
    "C#": [
        "/bin/**",
        "/obj/**",
        "*.user",
        "*.suo",
        "/.vs/**",
        "*.csproj",
        "*.sln",
    ],
    "Node.js": [
        "/node_modules/**",
        "package-lock.json",
        "yarn.lock",
        "*.log",
        "/build/**",
        "/dist/**",
        ".npmrc",
    ],
    "Generic": [
        "/.git/**",
        "/.vscode/**",
        "*.lock",
        "/logs/**",
        "*.tmp",
        "*.bak",
        "*.swp",
        "LICENSE",
        "README.md",
        "*.md",
    ],
}


# --- File Exclusion Logic ---
def is_excluded(item_path_normalized, exclusion_patterns):
    # item_path_normalized is like "foo/bar.txt" or "foo/baz/" (if it's a directory path being checked for pruning)
    # It's always relative to the scan root, without a leading '/'.
    item_name = os.path.basename(item_path_normalized.rstrip('/'))  # "bar.txt" or "baz"

    for pattern in exclusion_patterns:
        clean_pattern = pattern.strip().replace(os.sep, '/')
        if not clean_pattern:
            continue

        # Handle directory wildcard patterns like 'dir/**', '/dir/**'
        if clean_pattern.endswith('/**'):
            dir_base = clean_pattern[:-3]  # Removes '/**'

            if dir_base.startswith('/'):
                dir_base_no_slash = dir_base.lstrip('/')
                if (
                    item_path_normalized.startswith(dir_base_no_slash + '/') or item_path_normalized == dir_base_no_slash
                ):
                    return True
            else:
                if (
                    item_path_normalized.startswith(dir_base + '/') or item_path_normalized == dir_base
                ):
                    return True
                if (
                    ("/" + dir_base + "/") in ("/" + item_path_normalized)
                ):
                    return True
            continue

        # Handle exact paths from root (must start with /)
        if clean_pattern.startswith('/'):
            if item_path_normalized == clean_pattern.lstrip('/'):
                return True
            continue

        # Handle glob patterns (e.g., '*.txt', 'file?.log')
        if '*' in clean_pattern or '?' in clean_pattern:
            if '/' in clean_pattern:  # Pattern like 'some_dir/*.py' or '*/secrets.txt'
                if fnmatch.fnmatch(item_path_normalized, clean_pattern):
                    return True
            else:  # Pattern like '*.py' - applies to basename only
                if fnmatch.fnmatch(item_name, clean_pattern):
                    return True
            continue

        # Handle exact matches for filenames or relative paths
        if '/' in clean_pattern:  # Exact relative path like 'docs/README.md'
            if item_path_normalized == clean_pattern:
                return True
        else:  # Exact basename match like 'LICENSE'
            if item_name == clean_pattern:
                return True

    return False
