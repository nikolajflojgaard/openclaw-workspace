---
name: "playwright-webapp-qa"
description: "Verify local web apps with Playwright screenshots and checks."
---

# Playwright Webapp QA

Use this skill when building or reviewing a frontend app, website, dashboard, game, canvas, or interactive tool that should be verified in a browser.

## Workflow

1. Identify app framework, start command, expected route, and target viewports.
2. Start the dev server if needed, using an available port and leaving unrelated servers alone.
3. Open the app with Playwright or an equivalent browser automation tool.
4. Capture screenshots at desktop and mobile widths.
5. Check browser console and network failures.
6. Exercise core interactions: navigation, forms, buttons, menus, tabs, sliders, dialogs, keyboard focus, and error states as relevant.
7. For canvas/3D/game work, verify nonblank rendering with pixel checks and movement/interaction.
8. Inspect responsive layout for overlap, clipping, unreadable text, and unstable controls.
9. Fix issues or report them with screenshots and file references.
10. Stop only the dev server started for this task unless the user wants it left running.

## Suggested Viewports

- Desktop: 1440x900 or app-specific equivalent.
- Tablet: 768x1024 when layout changes matter.
- Mobile: 390x844 or 375x667 for tight checks.

## Evidence To Capture

Return:

- URL tested
- start command and port
- screenshot paths
- console/network issues
- interactions tested
- viewport results
- remaining gaps

## Quality Rules

- Do not rely on static code review for visual claims when the app can run.
- Do not ignore console errors from the app under test.
- Do not claim mobile readiness without a mobile screenshot or equivalent viewport check.
- For text-heavy UI, verify the longest visible labels fit.
- For generated assets, verify that referenced files actually load.

## Guardrails

- Do not interact with production sites or real accounts unless explicitly requested.
- Do not submit forms, send messages, make payments, or publish content during QA without explicit approval.
- Do not kill unrelated processes on shared ports; choose a different port when needed.
