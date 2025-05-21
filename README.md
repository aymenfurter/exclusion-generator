# GitHub Copilot Exclusion Generator

[![CI](https://github.com/aymenfurter/exclusion-generator/actions/workflows/ci.yml/badge.svg)](https://github.com/aymenfurter/exclusion-generator/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A tool to help generate GitHub Copilot exclusion rules for your repository, particularly focusing on files with potential PII (Personally Identifiable Information).

## Features

- Scan your repository for potential PII in text files
- Apply language-specific presets to automatically exclude common non-source files
- Customize exclusion patterns to match your project's needs
- Generate GitHub Copilot compatible exclusion rules for your repository

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aymenfurter/exclusion-generator.git
cd exclusion-generator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open the web interface (typically at http://localhost:7860)

3. Use the UI to:
   - Select your repository folder
   - Choose language presets for automatic exclusion patterns
   - Add custom exclusion patterns if needed
   - Configure PII detection sensitivity
   - Run the scan

4. Copy the generated exclusion rules into your GitHub Copilot configuration

## Configuration Options

- **Confidence Threshold**: Set the minimum confidence level (percentage) required for PII detection
- **Minimum PII Entities**: Set the minimum number of PII entities required to flag a file
- **PII Entity Types**: Select which types of PII to scan for (e.g., PERSON, EMAIL_ADDRESS, etc.)
- **Preset Exclusions**: Choose from language-specific presets to exclude common non-source files
- **Custom Exclusions**: Add comma-separated patterns to exclude additional files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run the tests to make sure everything works (`pytest`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.