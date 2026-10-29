// Markdown (docs/task-reports/*.md) -> Word (.docx). The Markdown stays the source of truth.
// usage (from docs/task-reports/tools):  npm install   then   node build-word.js ..
const fs = require("fs");
const path = require("path");
const { marked } = require("marked");
const sharp = require("sharp");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell, WidthType,
  ShadingType, AlignmentType, ImageRun, ExternalHyperlink, Footer, Header, PageNumber,
  TableOfContents, LevelFormat, BorderStyle, PageBreak, TableLayoutType,
} = require("docx");

const DIR = path.resolve(process.argv[2]);
const OUT_WORD = path.join(DIR, "word");
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134;           // A4, 2 cm margins
const TEXT_W = PAGE_W - 2 * MARGIN;                             // 9638 DXA
const IMG_MAX_W_PX = Math.round(TEXT_W / 1440 * 96);            // ~642 px at 96 dpi
const IMG_MAX_H_PX = 760;                                       // one slice fits a page with caption
const FONT = "Calibri", MONO = "Consolas";
const tmpDir = path.join(require("os").tmpdir(), "report-slices");
fs.mkdirSync(tmpDir, { recursive: true });

// ------------------------------------------------------------------ inline
function decode(s) {
  return s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
          .replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}
function inline(tokens, style = {}) {
  const runs = [];
  for (const t of tokens || []) {
    switch (t.type) {
      case "strong": runs.push(...inline(t.tokens, { ...style, bold: true })); break;
      case "em": runs.push(...inline(t.tokens, { ...style, italics: true })); break;
      case "codespan":
        runs.push(new TextRun({ text: decode(t.text), font: MONO, size: (style.size || 21) - 2,
                                shading: { type: ShadingType.CLEAR, fill: "F1F1F1" }, ...pick(style) }));
        break;
      case "link": {
        const kids = inline(t.tokens, { ...style, color: "1F4E9A", underline: {} });
        if (/^https?:/.test(t.href)) runs.push(new ExternalHyperlink({ link: t.href, children: kids }));
        else runs.push(...kids);
        break;
      }
      case "br": runs.push(new TextRun({ break: 1 })); break;
      case "del": runs.push(...inline(t.tokens, { ...style, strike: true })); break;
      case "escape": case "text":
        if (t.tokens && t.tokens.length) runs.push(...inline(t.tokens, style));
        else runs.push(new TextRun({ text: decode(t.text), font: FONT, ...pick(style) }));
        break;
      case "html": break;
      default: if (t.text) runs.push(new TextRun({ text: decode(t.text), font: FONT, ...pick(style) }));
    }
  }
  return runs;
}
function pick(s) {
  const o = {};
  for (const k of ["bold", "italics", "color", "underline", "size", "strike"]) if (s[k] !== undefined) o[k] = s[k];
  return o;
}

// ------------------------------------------------------------------ images
async function imageParas(src, mdFile, figCounter) {
  const file = path.resolve(path.dirname(mdFile), src);
  if (!fs.existsSync(file)) return [new Paragraph({ children: [new TextRun({ text: `[missing image: ${src}]`, color: "C00000" })] })];
  // Trim uniform borders (GitHub pages have wide blank margins), keep a small padding.
  const trimmed = await sharp(file).trim({ threshold: 12 }).toBuffer({ resolveWithObject: true });
  const tw = trimmed.info.width, th = trimmed.info.height;
  const padded = await sharp(trimmed.data).extend({ top: 8, bottom: 8, left: 8, right: 8,
                                                 background: { r: 255, g: 255, b: 255, alpha: 1 } }).png().toBuffer();
  const meta = { width: tw + 16, height: th + 16 };
  const scale = Math.min(1, IMG_MAX_W_PX / meta.width);
  const sliceSrcH = Math.floor(IMG_MAX_H_PX / scale);
  const parts = [];
  for (let top = 0, i = 0; top < meta.height; top += sliceSrcH, i++) {
    const h = Math.min(sliceSrcH, meta.height - top);
    if (h < 40 && i > 0) break;                               // ignore a sliver at the end
    let buf;
    if (top === 0 && h === meta.height) buf = padded;
    else buf = await sharp(padded).extract({ left: 0, top, width: meta.width, height: h }).png().toBuffer();
    parts.push({ buf, w: Math.round(meta.width * scale), h: Math.round(h * scale) });
  }
  return parts.map((p, i) => new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 80, after: 40 }, keepNext: true,
    children: [new ImageRun({ type: "png", data: p.buf, transformation: { width: p.w, height: p.h },
                              border: undefined })]
      .concat(parts.length > 1 ? [new TextRun({ text: ` (part ${i + 1} of ${parts.length})`, size: 16, color: "777777" })] : []),
  }));
}

// ------------------------------------------------------------------ blocks
const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
function table(t) {
  const n = t.header.length;
  const lens = t.header.map((h, i) => Math.max(h.text.length, ...t.rows.map(r => (r[i] ? r[i].text.length : 0))));
  const weights = lens.map(l => Math.max(6, Math.min(l, 70)));
  const sum = weights.reduce((a, b) => a + b, 0);
  let widths = weights.map(w => Math.floor(TEXT_W * w / sum));
  widths[n - 1] += TEXT_W - widths.reduce((a, b) => a + b, 0);
  const cell = (c, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA },
    margins: { top: 50, bottom: 50, left: 80, right: 80 },
    shading: head ? { type: ShadingType.CLEAR, fill: "1F3A5F" } : undefined,
    borders: { top: border, bottom: border, left: border, right: border },
    children: [new Paragraph({ spacing: { before: 0, after: 0 },
      children: inline(c.tokens, head ? { bold: true, color: "FFFFFF", size: 18 } : { size: 18 }) })],
  });
  return new Table({
    width: { size: TEXT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ tableHeader: true, children: t.header.map((c, i) => cell(c, i, true)) }),
           ...t.rows.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false)) }))],
  });
}
function code(text) {
  return text.split("\n").map((line, i, all) => new Paragraph({
    spacing: { before: i === 0 ? 80 : 0, after: i === all.length - 1 ? 120 : 0, line: 240 },
    shading: { type: ShadingType.CLEAR, fill: "F3F3F3" }, indent: { left: 120, right: 120 },
    keepLines: true,
    children: [new TextRun({ text: line.length ? line : " ", font: MONO, size: 16 })],
  }));
}
async function blocks(tokens, mdFile, ctx, level = 0) {
  const out = [];
  for (const t of tokens) {
    switch (t.type) {
      case "heading": {
        const lv = Math.min(t.depth + ctx.headingShift, 4);
        const H = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][lv];
        out.push(new Paragraph({ heading: H, keepNext: true, pageBreakBefore: ctx.breakBeforeH1 && t.depth === 1 && ctx.seenH1++ > 0,
                                 children: inline(t.tokens) }));
        break;
      }
      case "paragraph": {
        const img = t.tokens.length === 1 && t.tokens[0].type === "image" ? t.tokens[0] : null;
        if (img) { out.push(...await imageParas(img.href, mdFile)); break; }
        const isCaption = /^\*Figure \d/.test(t.raw);
        out.push(new Paragraph({ spacing: { after: isCaption ? 60 : 120 }, keepNext: isCaption,
                                 children: inline(t.tokens, isCaption ? { size: 19, color: "404040" } : {}) }));
        break;
      }
      case "list": {
        const ref = t.ordered ? ctx.nextOrdered() : "bullets";   // one sequence per list
        for (const item of t.items) {
          const kids = [];
          const inl = [];
          for (const sub of item.tokens) {
            if (sub.type === "text" || sub.type === "paragraph") inl.push(...(sub.tokens || [{ type: "text", text: sub.text }]));
            else kids.push(sub);
          }
          const prefix = item.task ? [new TextRun({ text: item.checked ? "â˜‘ " : "â˜ ", font: "Segoe UI Symbol" })] : [];
          out.push(new Paragraph({
            numbering: { reference: ref, level },
            spacing: { after: 60 }, children: prefix.concat(inline(inl)),
          }));
          for (const k of kids) {
            if (k.type === "list") out.push(...await blocks([k], mdFile, ctx, level + 1));
            else out.push(...await blocks([k], mdFile, ctx, level));
          }
        }
        break;
      }
      case "table": out.push(table(t)); out.push(new Paragraph({ spacing: { after: 80 }, children: [] })); break;
      case "code": out.push(...code(t.text)); break;
      case "blockquote":
        for (const b of await blocks(t.tokens, mdFile, ctx, level)) out.push(b);
        break;
      case "hr": out.push(new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "BFBFBF" } }, children: [] })); break;
      case "space": break;
      case "html": break;
      default: if (t.text) out.push(new Paragraph({ children: [new TextRun(decode(t.text))] }));
    }
  }
  return out;
}

// ------------------------------------------------------------------ document
function makeCtx(opts) {
  let n = 0;
  return { headingShift: opts.headingShift || 0, breakBeforeH1: opts.breakBeforeH1, seenH1: 0,
           nextOrdered: () => `num${n++ % 200}` };
}
const numbering = {
  config: [
    { reference: "bullets", levels: [0, 1, 2].map(l => ({ level: l, format: LevelFormat.BULLET, text: ["â€¢", "â€“", "â€¢"][l],
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360 + 360 * l, hanging: 260 } } } })) },
    ...Array.from({ length: 200 }, (_, i) => ({ reference: `num${i}`, levels: [0, 1, 2].map(l => ({ level: l, format: LevelFormat.DECIMAL,
        text: `%${l + 1}.`, alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360 + 360 * l, hanging: 300 } } } })) })),
  ],
};
const styles = {
  default: { document: { run: { font: FONT, size: 21 }, paragraph: { spacing: { line: 276 } } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 32, bold: true, color: "1F3A5F", font: FONT }, paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 26, bold: true, color: "1F3A5F", font: FONT }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 22, bold: true, color: "333333", font: FONT }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
    { id: "Heading4", name: "Heading 4", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 21, bold: true, italics: true, font: FONT }, paragraph: { spacing: { before: 120, after: 60 }, outlineLevel: 3 } },
  ],
};
function section(children, headerText) {
  return {
    properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: headerText, size: 16, color: "808080" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: ["Page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], size: 16, color: "808080" })] })] }) },
    children,
  };
}
async function mdToBlocks(file, opts) {
  const tokens = marked.lexer(fs.readFileSync(file, "utf8"));
  return blocks(tokens, file, makeCtx(opts));
}
async function save(doc, file) {
  fs.writeFileSync(file, await Packer.toBuffer(doc));
  console.log("wrote", path.relative(DIR, file), Math.round(fs.statSync(file).size / 1024) + " KB");
}

const TITLE = "CI/CD Pipeline for a Hotel Room Booking Portal";
const tasks = fs.readdirSync(DIR).filter(f => /^task-\d\d-.*\.md$/.test(f)).sort();
const wordNames = [
  "Task_01_Problem_Definition_and_Scope", "Task_02_Agile_Planning_and_DevOps_Workflow",
  "Task_03_Requirements_Architecture_and_Setup", "Task_04_Git_and_GitHub_Initialization",
  "Task_05_Feature_Development_and_Branching", "Task_06_MVP_Completion_and_Collaboration",
  "Task_07_Jenkins_Installation_and_CI", "Task_08_Pipeline_as_Code_and_Deployment",
  "Task_09_Selenium_Test_Design_and_Execution", "Task_10_Continuous_Testing_in_Jenkins",
  "Task_11_Docker_Image_and_Container_Lifecycle", "Task_12_Jenkins_Docker_Continuous_Deployment",
  "Task_13_Configuration_Management_with_Ansible", "Task_14_Provisioning_Idempotency_and_Rollback",
  "Task_15_Final_End_to_End_Release"];

(async () => {
  fs.mkdirSync(OUT_WORD, { recursive: true });
  // individual task documents
  for (let i = 0; i < tasks.length; i++) {
    const children = await mdToBlocks(path.join(DIR, tasks[i]), {});
    await save(new Document({ creator: "Student", title: wordNames[i].replace(/_/g, " "), styles, numbering,
                              sections: [section(children, `${TITLE} - Task ${i + 1}`)] }),
               path.join(OUT_WORD, wordNames[i] + ".docx"));
  }
  // combined report
  const cover = [
    new Paragraph({ spacing: { before: 3000 }, alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: TITLE, bold: true, size: 48, color: "1F3A5F" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300 },
      children: [new TextRun({ text: "Complete DevOps Project Report - all 15 tasks", size: 30 })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 600 },
      children: [new TextRun({ text: "Python / Flask - Git & GitHub - Jenkins - pytest & Selenium - Docker - Ansible", size: 22, color: "404040" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1800 },
      children: [new TextRun({ text: "Evidence verified on 2026-10-20. Generated from docs/task-reports/*.md.", size: 20, color: "606060" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120 },
      children: [new TextRun({ text: "Repository: https://github.com/KemNxts/hotel-room-booking-cicd", size: 20, color: "606060" })] }),
    new Paragraph({ children: [new PageBreak()] }),
    new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Contents", bold: true, size: 32, color: "1F3A5F" })] }),
    new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-1" }),
  ];
  const body = [];
  for (const f of ["README.md", "00-project-audit.md", ...tasks, "VIVA_CHEAT_SHEET.md", "screenshot-index.md"]) {
    body.push(new Paragraph({ children: [new PageBreak()] }));
    body.push(...await mdToBlocks(path.join(DIR, f), {}));
  }
  await save(new Document({ creator: "Student", title: "Complete DevOps Project Report", styles, numbering, features: { updateFields: true },
                            sections: [section(cover.concat(body), TITLE)] }),
             path.join(DIR, "Complete_DevOps_Project_Report.docx"));
})().catch(e => { console.error(e); process.exit(1); });

