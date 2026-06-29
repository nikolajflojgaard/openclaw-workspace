---
name: "office-doc-workflow"
description: "Work safely with DOCX, XLSX, PPTX, and PDFs."
---

# Office Document Workflow

Use this skill when the user asks to read, summarize, edit, generate, convert, compare, or extract data from Word, Excel, PowerPoint, or PDF documents.

## Default Posture

- Preserve originals.
- Use structured parsers and document APIs when available.
- Make a working copy before edits.
- Validate generated documents by reopening or extracting content.
- Use the existing `nano-pdf` skill for natural-language PDF editing when it fits better.

## Workflow

1. Identify file type, target output, and whether formatting must be preserved.
2. Copy the source file to a working path when editing.
3. Inspect metadata and structure before changing content.
4. Choose the least lossy method:
   - DOCX: use document-aware libraries or OOXML inspection rather than plain unzip edits unless necessary.
   - XLSX: preserve formulas, sheets, charts, and cell types; avoid CSV conversion unless the user only needs raw data.
   - PPTX: preserve slide layouts, masters, images, and speaker notes where possible.
   - PDF: use extraction/editing tools suited to text, tables, annotations, or page operations.
5. Perform the requested extraction, edit, generation, or conversion.
6. Validate by opening, parsing, or rendering the output and checking key content.
7. Report any formatting risks or unsupported elements.

## Common Checks

- Text extraction: confirm expected headings, tables, and counts.
- Edits: compare before/after content and ensure unrelated sections did not change.
- Spreadsheets: check formulas, date/currency formats, hidden sheets, filters, merged cells, and row counts.
- Presentations: check slide count, image presence, title text, notes, and layout consistency.
- PDFs: check page count, text extraction, visual rendering for changed pages, and file size.

## Guardrails

- Do not overwrite source documents.
- Do not strip formulas, comments, tracked changes, speaker notes, or metadata unless explicitly requested.
- Do not claim formatting preservation without validation.
- Do not paste large private document contents into external services without approval.
- For legal, financial, or medical documents, preserve exact wording and flag uncertainty.
