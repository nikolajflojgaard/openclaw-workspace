import { mkdir, mkdtemp, readFile, rm, stat, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawn } from 'node:child_process';

function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      ...options,
    });
    child.on('error', reject);
    child.on('exit', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${command} exited with code ${code}`));
    });
  });
}

function findChrome() {
  const candidates = [
    process.env.CHROME_BIN,
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
  ].filter(Boolean);

  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }

  throw new Error('No Chrome/Chromium executable found. Set CHROME_BIN or install Google Chrome.');
}

function parseArgs(rawArgs) {
  const options = {
    htmlOnly: false,
    titlePage: true,
    title: '',
    subtitle: 'API Specification',
    system: '',
    version: '',
    brandName: 'OpenAPI Spec Workflow',
    date: new Date().toISOString().slice(0, 10),
    positional: [],
  };

  for (let i = 0; i < rawArgs.length; i += 1) {
    const arg = rawArgs[i];
    if (arg === '--html') options.htmlOnly = true;
    else if (arg === '--no-title-page') options.titlePage = false;
    else if (arg === '--title') options.title = rawArgs[++i] || '';
    else if (arg === '--subtitle') options.subtitle = rawArgs[++i] || '';
    else if (arg === '--system') options.system = rawArgs[++i] || '';
    else if (arg === '--version') options.version = rawArgs[++i] || '';
    else if (arg === '--brand-name') options.brandName = rawArgs[++i] || '';
    else if (arg === '--date') options.date = rawArgs[++i] || options.date;
    else options.positional.push(arg);
  }

  return options;
}

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function inferTitle(inputPath) {
  return path.basename(inputPath, path.extname(inputPath)).replace(/[-_]+/g, ' ');
}

function buildWrapperHtml(bodyHtml, options, inputPath) {
  const title = escapeHtml(options.title || inferTitle(inputPath));
  const subtitle = escapeHtml(options.subtitle || 'API Specification');
  const system = escapeHtml(options.system || '');
  const version = escapeHtml(options.version || '');
  const date = escapeHtml(options.date || '');
  const brandName = escapeHtml(options.brandName || '');

  const titlePage = options.titlePage
    ? `
  <section class="title-page">
    <div class="title-page__art title-page__art--left"></div>
    <div class="title-page__art title-page__art--right"></div>
    <div class="title-page__inner">
      <div class="title-page__eyebrow">${brandName}</div>
      <h1>${title}</h1>
      <p class="title-page__subtitle">${subtitle}</p>
      <div class="title-page__meta">
        ${system ? `<div><span>System</span><strong>${system}</strong></div>` : ''}
        ${version ? `<div><span>Version</span><strong>${version}</strong></div>` : ''}
        ${date ? `<div><span>Date</span><strong>${date}</strong></div>` : ''}
      </div>
    </div>
    <div class="title-page__footer-mark">${brandName}</div>
  </section>
  <div class="page-break"></div>`
    : '';

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --ink: #17285f;
      --muted: #3f4b73;
      --line: #c5d7ee;
      --accent: #3f5bdc;
      --shape-left: #c5d7ee;
      --shape-right: #7fa6dc;
    }
    * { box-sizing: border-box; }
    body { margin: 0; color: var(--ink); background: white; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .title-page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      padding: 56px 56px 96px;
      background: linear-gradient(180deg, #fff, #f8fafc);
      position: relative;
      overflow: hidden;
    }
    .title-page__art {
      position: absolute;
      top: -120px;
      border-radius: 999px;
      z-index: 0;
    }
    .title-page__art--left {
      left: -180px;
      width: 720px;
      height: 320px;
      background: var(--shape-left);
      transform: rotate(-8deg);
    }
    .title-page__art--right {
      right: -120px;
      width: 420px;
      height: 240px;
      background: var(--shape-right);
      transform: rotate(12deg);
    }
    .title-page__inner {
      width: 100%;
      max-width: 860px;
      padding-top: 140px;
      position: relative;
      z-index: 1;
    }
    .title-page__eyebrow {
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 20px;
    }
    h1 { font-size: 40px; line-height: 1.08; margin: 0 0 12px; max-width: 14ch; }
    .title-page__subtitle { font-size: 18px; line-height: 1.5; color: var(--muted); margin: 0 0 36px; }
    .title-page__meta { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 28px; }
    .title-page__meta div { border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }
    .title-page__meta span { display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
    .title-page__meta strong { font-size: 15px; }
    .title-page__footer-mark {
      position: absolute;
      bottom: 34px;
      left: 50%;
      transform: translateX(-50%);
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: lowercase;
      z-index: 1;
    }
    .page-break { break-after: page; page-break-after: always; }
    @page { margin: 0; }
  </style>
</head>
<body>
${titlePage}
${bodyHtml}
</body>
</html>`;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const [inputArg, outputArg] = options.positional;

  if (!inputArg) {
    console.error('Usage: node render_openapi_pdf.mjs [options] <input.yaml> <output.pdf|output.html>');
    process.exit(1);
  }

  const cwd = process.cwd();
  const inputPath = path.resolve(cwd, inputArg);
  const outputPath = path.resolve(cwd, outputArg || (options.htmlOnly ? './openapi-spec.html' : './openapi-spec.pdf'));

  await mkdir(path.dirname(outputPath), { recursive: true });

  const tmpRoot = await mkdtemp(path.join(tmpdir(), 'openapi-skill-'));
  const redocHtmlPath = path.join(tmpRoot, 'redoc.html');
  const wrappedHtmlPath = path.join(tmpRoot, 'wrapped.html');

  try {
    await run('npx', ['@redocly/cli', 'build-docs', inputPath, '-o', redocHtmlPath]);

    const redocHtml = await readFile(redocHtmlPath, 'utf8');
    const wrappedHtml = buildWrapperHtml(redocHtml, options, inputPath);

    if (options.htmlOnly) {
      await writeFile(outputPath, wrappedHtml, 'utf8');
      console.log(`HTML written to ${outputPath}`);
      return;
    }

    await writeFile(wrappedHtmlPath, wrappedHtml, 'utf8');

    const chrome = findChrome();
    await run(chrome, [
      '--headless=new',
      '--disable-gpu',
      '--no-first-run',
      '--allow-file-access-from-files',
      '--enable-local-file-accesses',
      '--run-all-compositor-stages-before-draw',
      '--virtual-time-budget=12000',
      `--print-to-pdf=${outputPath}`,
      `file://${wrappedHtmlPath}`,
    ]);

    const pdfStat = await stat(outputPath);
    if (!pdfStat.size) throw new Error('PDF generation completed but output file is empty.');

    console.log(`PDF written to ${outputPath}`);
  } finally {
    await rm(tmpRoot, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
