# Rebuilding the Word / PDF reports

The Markdown files in `docs/task-reports/` are the source. After editing them:

```powershell
cd docs\task-reports\tools
npm install                 # first time only (docx, marked, sharp)
node build-word.js ..       # -> ..\Complete_DevOps_Project_Report.docx and ..\word\Task_XX_*.docx
```

Then open `Complete_DevOps_Project_Report.docx` in Microsoft Word, right-click the
table of contents -> *Update Field -> Update entire table*, and
*File -> Save As -> PDF* to refresh `Complete_DevOps_Project_Report.pdf`.

`render-pdf-pages.ps1` renders PDF pages to PNG (Windows built-in PDF engine) to
check the layout: `.\render-pdf-pages.ps1 -Pdf ..\Complete_DevOps_Project_Report.pdf -OutDir pages -Pages 1,2,3`.
