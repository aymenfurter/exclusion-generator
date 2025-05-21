import os
import gradio as gr
from .exclusions import (
    COMMON_NON_TEXT_EXCLUSIONS, EXCLUSION_PRESETS, is_excluded
)
from .presidio_analyzer_setup import get_presidio_analyzer


# --- Core Scanning Logic ---
def scan_directory_for_pii(
    directory_path: str,
    selected_presets: list[str] | None,
    custom_exclusions_str: str,
    confidence_threshold: float = 60,
    min_entities_threshold: int = 2,
    selected_entity_types: list[str] = ["PERSON"],
    progress: gr.Progress = gr.Progress(track_tqdm=True)
):
    if not directory_path or not os.path.isdir(directory_path):
        return (
            "Error: Provided path is not a valid directory. "
            "Please enter a valid directory path."
        )

    try:
        analyzer = get_presidio_analyzer()
    except RuntimeError as e:
        return f"Error initializing PII analyzer: {e}"

    # Ensure we have at least one entity type selected
    if not selected_entity_types:
        return "Error: At least one PII entity type must be selected for scanning."

    all_exclusion_patterns = list(set(COMMON_NON_TEXT_EXCLUSIONS))

    preset_patterns = []
    if selected_presets:
        for preset_name in selected_presets:
            preset_patterns.extend(EXCLUSION_PRESETS.get(preset_name, []))
    all_exclusion_patterns.extend(
        p for p in preset_patterns if p not in all_exclusion_patterns
    )

    if custom_exclusions_str:
        custom_patterns = [
            p.strip() for p in custom_exclusions_str.split(',') if p.strip()
        ]
        all_exclusion_patterns.extend(
            p for p in custom_patterns if p not in all_exclusion_patterns
        )

    pii_files_output_lines = []
    pii_found_count = 0
    scanned_files_info = {}  # Store details about PII found in each file

    normalized_directory_path = os.path.normpath(directory_path)

    # Convert threshold from percentage to decimal if passed as percentage
    if confidence_threshold > 1:
        confidence_threshold = confidence_threshold / 100.0
    
    # Ensure min_entities_threshold is an integer
    min_entities_threshold = max(1, int(min_entities_threshold))

    progress(0, desc="Counting files to scan...")
    candidate_files_to_scan_paths = []

    paths_to_walk = [
        (
            normalized_directory_path,
            list(next(os.walk(normalized_directory_path))[1]),
            list(next(os.walk(normalized_directory_path))[2])
        )
    ]

    idx = 0
    while idx < len(paths_to_walk):
        root, dirs, files = paths_to_walk[idx]
        idx += 1

        current_walk_dir_rel_path = os.path.relpath(root, normalized_directory_path)
        current_walk_dir_rel_path_normalized = ""
        if current_walk_dir_rel_path != '.':
            current_walk_dir_rel_path_normalized = (
                current_walk_dir_rel_path.replace(os.sep, '/') + '/'
            )

        original_dirs = list(dirs)
        dirs[:] = []

        for d_name in original_dirs:
            dir_abs_path = os.path.join(root, d_name)
            dir_item_path_normalized = (
                current_walk_dir_rel_path_normalized + d_name.replace(os.sep, '/') + '/'
            )
            if not is_excluded(dir_item_path_normalized, all_exclusion_patterns):
                dirs.append(d_name)
                try:
                    sub_root, sub_dirs, sub_files = next(os.walk(dir_abs_path))
                    paths_to_walk.append((sub_root, list(sub_dirs), list(sub_files)))
                except StopIteration:
                    pass

        for file_name in files:
            file_path_abs = os.path.join(root, file_name)
            relative_file_path = os.path.relpath(file_path_abs, normalized_directory_path)
            relative_file_path_normalized = relative_file_path.replace(os.sep, '/')

            if not is_excluded(relative_file_path_normalized, all_exclusion_patterns):
                candidate_files_to_scan_paths.append(file_path_abs)

    total_files_to_scan = len(candidate_files_to_scan_paths)
    if total_files_to_scan == 0:
        return "Scan complete. No files to scan after applying exclusions."

    files_processed_count = 0

    for i, file_path_abs in enumerate(candidate_files_to_scan_paths):
        relative_file_path = os.path.relpath(
            file_path_abs, normalized_directory_path
        )
        relative_file_path_normalized = relative_file_path.replace(os.sep, '/')

        progress(
            (i + 1) / total_files_to_scan,
            desc=(
                f"Scanning ({i+1}/{total_files_to_scan}): "
                f"{relative_file_path_normalized}"
            ),
        )

        files_processed_count += 1
        try:
            with open(
                file_path_abs,
                "r",
                encoding="utf-8",
                errors="ignore",
            ) as f_content:
                content = f_content.read(1_000_000)  # Limit read size to 1MB
        except Exception as e:
            print(
                f"Error processing file {file_path_abs}: {e}"
            )
            pii_files_output_lines.append(
                f"# Error processing: {relative_file_path_normalized} - {e}"
            )
            continue

        if not content.strip():
            continue

        # Analyze file content for PII
        analyzer_results = analyzer.analyze(
            text=content,
            language='en',
            entities=selected_entity_types  # Only analyze for selected entity types
        )
        
        # Filter results by user-defined confidence threshold
        significant_results = [r for r in analyzer_results if r.score >= confidence_threshold]
        
        # Only flag files with enough significant PII detections (user-defined threshold)
        if len(significant_results) >= min_entities_threshold:
            pii_found_count += 1
            
            # Collect information about detected PII types
            pii_types = {}
            for result in significant_results:
                entity_type = result.entity_type
                if entity_type in pii_types:
                    pii_types[entity_type] += 1
                else:
                    pii_types[entity_type] = 1
            
            # Store detailed information
            scanned_files_info[relative_file_path_normalized] = {
                'pii_count': len(significant_results),
                'pii_types': pii_types
            }
            
            # Format as GitHub Copilot expects
            if relative_file_path_normalized.startswith("/"):
                path_for_comment = relative_file_path_normalized
            else:
                path_for_comment = f"/{relative_file_path_normalized}"
            
            # Include PII type information in the comment
            pii_description = ", ".join([f"{count} {pii_type}"
                                        for pii_type, count in pii_types.items()])
            
            pii_files_output_lines.append(
                f"# Ignore the `{path_for_comment}` file in this repository (Contains: {pii_description})."
            )
            pii_files_output_lines.append(
                f"- \"{path_for_comment}\""
            )

    entity_types_str = ", ".join(selected_entity_types)
    
    summary = (
        f"# Scan complete: Found significant PII in {pii_found_count} of {files_processed_count} files.\n"
        f"# Settings: {min_entities_threshold}+ PII entities with confidence >= {confidence_threshold*100:.0f}%\n"
        f"# PII types scanned: {entity_types_str}\n\n"
    )
    if not pii_files_output_lines:
        return summary + (
            "# No significant PII found in scannable files, or all files were excluded."
        )

    return summary + "\n".join(pii_files_output_lines)
