---
name: openapi-spec-workflow
description: Create Swagger/OpenAPI YAML from requirements, design docs, or endpoint descriptions, and generate a human-readable API specification PDF from that YAML. Use when the user wants to draft an API contract, turn a final design into OpenAPI, validate/specify endpoints and schemas, or render an OpenAPI YAML/JSON file into reviewable HTML/PDF documentation.
---

# OpenAPI Spec Workflow

Use this skill for two related jobs:
- write or refine an OpenAPI spec
- turn an OpenAPI spec into a readable API specification PDF

## Default workflow

### 1. Decide the starting point

If the user gives:
- a requirement brief
- a final design doc
- endpoint notes
- an existing partial Swagger/OpenAPI file

then first decide whether the task is:
- **authoring** a new spec
- **repairing** an existing spec
- **rendering** a finished spec into PDF

### 2. If authoring YAML, write the contract first

Before generating the PDF, make sure the YAML is good enough to stand on its own.

Minimum bar:
- `openapi` version
- `info`
- `servers` when known
- paths and operations
- request/response schemas
- auth model when relevant
- error responses
- reusable components where useful

Read `references/openapi-authoring.md` when you need the checklist and skeleton.

### 3. Keep the YAML as source of truth

Do not hand-edit a PDF to express contract changes.
Always update the YAML first, then regenerate HTML/PDF.

### 4. Generate the PDF from the YAML

Use:
- `scripts/render_openapi_pdf.mjs`

It renders docs with Redocly and prints them to PDF with headless Chrome.

Example:

```bash
node skills/openapi-spec-workflow/scripts/render_openapi_pdf.mjs ./api.yaml ./api-spec.pdf
```

With a cleaner title page:

```bash
node skills/openapi-spec-workflow/scripts/render_openapi_pdf.mjs \
  --title "Customer Address API" \
  --subtitle "API Specification" \
  --system "Customer Platform" \
  --version "v1.0" \
  ./api.yaml \
  ./api-spec.pdf
```

Optional HTML-only output:

```bash
node skills/openapi-spec-workflow/scripts/render_openapi_pdf.mjs --html ./api.yaml ./api-spec.html
```

### 5. Brand later, not prematurely

Default to a clean readable PDF first.
When the user later provides logos, fonts, or brand rules, add them under `assets/` and update the render path.

Until then, use the built-in neutral cover page instead of shipping raw Redoc with no front matter.

## TDC NET default document pattern

When producing TDC NET-style API specifications, default to this combined document structure:

1. standalone **Table of content** page
2. **1. Change log** as a real Version / Date / Description table
3. **2. Overview**
4. **3. Interaction with TDC NET API**
   - **3.1 Security setup**
   - **3.2 Documentation**
   - **3.3 Chinese walls**
5. **4. The specific API**
   - **4.1 / 4.2 / 4.n** entries for each endpoint
   - each entry should list method + path + plain-language purpose
6. **5. Attachments**
   - plain-text JSON/XML examples only
   - do not use screenshots or image payload examples

Keep this as one combined document, not split docs, unless the user explicitly asks otherwise.

## Authoring rules

- Prefer explicit schemas over vague descriptions
- Use stable operation ids
- Keep naming tied to the business capability, not internal sludge
- Model real errors, not only happy-path `200`
- Do not invent auth/security details when they are unknown; mark them clearly
- If the design is not complete enough for a real spec, say so and draft the cleanest honest partial spec possible

## Output expectations

When producing a spec from a design, the result should be good enough that:
- engineering can discuss the contract
- stakeholders can review the PDF
- future edits happen in YAML, not scattered docs

## Resources

### `references/openapi-authoring.md`
Use when drafting or tightening a spec.

### `references/openapi-skeleton.yaml`
Use as a starting structure when creating a new spec quickly.

### `scripts/render_openapi_pdf.mjs`
Use to generate HTML or PDF from Swagger/OpenAPI YAML/JSON.

### `references/pdf-branding-notes.md`
Use when preparing later branding changes so the skill knows what assets and rules to collect.
