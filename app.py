import gradio as gr
from ghcp_exclusion_builder.scanner import scan_directory_for_pii
from ghcp_exclusion_builder.exclusions import (
    COMMON_NON_TEXT_EXCLUSIONS, EXCLUSION_PRESETS
)
from ghcp_exclusion_builder.presidio_analyzer_setup import (
    get_presidio_analyzer, PII_ENTITY_TYPES
)


def update_effective_exclusions_display(
    selected_presets_list, custom_exclusions_str
):
    effective_patterns = set(COMMON_NON_TEXT_EXCLUSIONS)

    if selected_presets_list:
        for preset_name in selected_presets_list:
            patterns = EXCLUSION_PRESETS.get(preset_name, [])
            effective_patterns.update(patterns)

    if custom_exclusions_str:
        custom_list = [
            p.strip() for p in custom_exclusions_str.split(',') if p.strip()
        ]
        effective_patterns.update(custom_list)

    return ", ".join(sorted(list(effective_patterns)))


def main():
    try:
        get_presidio_analyzer()
    except RuntimeError as e:
        print(f"Failed to initialize Presidio Analyzer on startup: {e}")

    with gr.Blocks() as iface:
        gr.Markdown(
            "## PII Scanner & GitHub Copilot Exclusion Generator\n"
            "Scans a directory for files containing PII using Microsoft Presidio.\n"
            "Generates exclusion rules in GitHub Copilot format for identified files.\n"
            "Common non-text files (images, archives, binaries, etc.)\n"
            "are always excluded by default. "
        )

        with gr.Row():
            directory_path_input = gr.Textbox(
                label="Directory Path to Scan",
                placeholder="/path/to/your/project_root"
            )

        with gr.Row():
            with gr.Column(scale=1):
                presets_checkboxgroup = gr.CheckboxGroup(
                    choices=list(EXCLUSION_PRESETS.keys()),
                    label="Exclusion Presets",
                    info=(
                        "Select presets to exclude common project files/"
                        "folders."
                    )
                )
            with gr.Column(scale=1):
                custom_exclusions_textbox = gr.Textbox(
                    label="Custom Exclusions (comma-separated)",
                    placeholder=(
                        "e.g., /specific_folder/**, *.tmp, *.bak, /build/**, "
                        "/dist/**, *.log"
                    )
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                confidence_threshold = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=60,
                    step=1,
                    label="Confidence Threshold (%)",
                    info="Only consider PII detections with confidence above this threshold"
                )
            with gr.Column(scale=1):
                min_entities_threshold = gr.Number(
                    value=2,
                    precision=0,
                    label="Minimum PII Entities",
                    info="Minimum number of PII entities required to flag a file",
                    minimum=1,
                    maximum=100
                )
        
        with gr.Row():
            entity_types_checkboxgroup = gr.CheckboxGroup(
                choices=PII_ENTITY_TYPES,
                value=["PERSON"],  # Default to PERSON only
                label="PII Entity Types to Detect",
                info="Select which types of PII entities to detect in files"
            )

        effective_patterns_display = gr.Textbox(
            label="Effective Exclusion Patterns (Read-only)",
            interactive=False,
            lines=3
        )

        scan_button = gr.Button("Scan for PII and Generate Exclusions")

        output_textbox = gr.Textbox(
            label="Generated GitHub Copilot Exclusion Rules",
            lines=15,
            show_copy_button=True
        )

        presets_checkboxgroup.change(
            fn=update_effective_exclusions_display,
            inputs=[presets_checkboxgroup, custom_exclusions_textbox],
            outputs=effective_patterns_display
        )
        custom_exclusions_textbox.change(
            fn=update_effective_exclusions_display,
            inputs=[presets_checkboxgroup, custom_exclusions_textbox],
            outputs=effective_patterns_display
        )

        iface.load(
            fn=update_effective_exclusions_display,
            inputs=[presets_checkboxgroup, custom_exclusions_textbox],
            outputs=effective_patterns_display
        )

        scan_button.click(
            fn=scan_directory_for_pii,
            inputs=[
                directory_path_input,
                presets_checkboxgroup,
                custom_exclusions_textbox,
                confidence_threshold,
                min_entities_threshold,
                entity_types_checkboxgroup
            ],
            outputs=output_textbox
        )

    iface.launch()


if __name__ == "__main__":
    main()
