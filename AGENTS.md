# AGENTS.md

## Project

This repository uses AI-assisted reading, analysis, and research on historical materials.

Base analysis on primary materials in `corpus/`. Write final reports to `reports/`.

## Directories

- `corpus/`: source historical texts. Treat these files as the evidence base.
- `reports/`: finished analysis reports and user-facing research outputs.
- `debug_agent/`: working files for agent runs, including scripts, notes, extracts, and intermediate data.

## Working Rules

- Preserve the research process when useful. Put temporary scripts and intermediate outputs in `debug_agent/`, not `/tmp`.
- Do not delete `debug_agent/` artifacts just because the immediate task is finished. They may be kept for later review or manually added to git.
- Keep reports evidence-grounded. Cite source files and, when practical, include searchable quoted snippets or location notes.
- Prefer reproducible scripts for repeated extraction, counting, filtering, or comparison work.
- Keep changes focused on the requested analysis or supporting workflow.

## Markdown

- Keep Markdown concise and readable.
- Leave one blank line after every heading before body text or lists.
- Insert one blank line between a paragraph ending with `:` and the following list.
- Use ASCII punctuation marks only, including in Chinese text.
- Put a single space after ASCII punctuation marks.
