# Changelog

All notable changes to this project are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] - 2026-10-01

### Added
- Colorful output with [rich](https://github.com/Textualize/rich): stats panel, scanning spinner, styled prompts
- File and folder sizes shown right in the tree
- Icons and colors by file type
- `requirements.txt`, `test_arch_analyzer.py`, CI on Windows / Linux / macOS
- MIT license, English README, contributing guide, issue templates

### Fixed
- Broken tree connectors on nested levels (files lost their `├──` / `└──` branches)

### Changed
- Script renamed from `python arch_analyzer.py` to `arch_analyzer.py`
- Requires Python 3.9+ and `rich`

## [1.0.0] - 2026-01-05

- First version: interactive project structure analyzer with ASCII tree and stats

[2.0.0]: https://github.com/Navruzbek05/project-tree-analyzer/releases/tag/v2.0.0
