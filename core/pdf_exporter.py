"""
ApexPilot AI - Native Local PDF Exporter Engine
================================================
Generates professional vector PDF records of interview questions, coding solutions,
STAR behavioral answers, and full session transcripts directly to local storage.
Utilizes hardware-accelerated QPdfWriter and QTextDocument.
"""

import sys
import os
import re
import html
from pathlib import Path
from datetime import datetime
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument, QPdfWriter, QPageSize, QPageLayout
from PySide6.QtCore import QMarginsF

logger = logging.getLogger("ApexPilot.PDF")

INTERVIEWS_DIR = Path(__file__).resolve().parent.parent / "saved_interviews"
INTERVIEWS_DIR.mkdir(parents=True, exist_ok=True)


class PDFExporter:
    """Exports interview questions and answers to structured PDF documents."""

    def __init__(self, output_dir: Path = INTERVIEWS_DIR):
        self.output_dir = output_dir

    def export_qa_pdf(self, question: str, answer: str, mode: str = "stealth_coder", provider: str = "local") -> Path:
        """
        Exports a single Question & Answer exchange to a beautifully styled PDF.
        Returns the path to the created PDF file.
        """
        app = QApplication.instance() or QApplication(sys.argv)

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_q_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', question[:30]).strip('_')
        if not safe_q_slug:
            safe_q_slug = "interview_qa"

        filename = f"{timestamp_str}_{safe_q_slug}.pdf"
        pdf_path = self.output_dir / filename

        # Format markdown answer to clean HTML for QTextDocument
        formatted_html = self._build_qa_html(question, answer, mode, provider)

        try:
            doc = QTextDocument()
            doc.setHtml(formatted_html)

            writer = QPdfWriter(str(pdf_path))
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            # Set 15mm margins
            layout = QPageLayout()
            layout.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            layout.setOrientation(QPageLayout.Orientation.Portrait)
            layout.setMargins(QMarginsF(12, 12, 12, 12))
            writer.setPageLayout(layout)

            doc.print_(writer)
            logger.info(f"Successfully generated interview PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            return None

    def export_session_pdf(self, transcript_entries: list[dict]) -> Path:
        """Exports the entire interview session transcript into a consolidated master PDF report."""
        app = QApplication.instance() or QApplication(sys.argv)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_full_{timestamp_str}.pdf"
        pdf_path = self.output_dir / filename

        body_html = "<h1>ApexPilot AI - Complete Interview Session Transcript</h1>"
        body_html += f"<p><b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p><hr/>"

        for idx, entry in enumerate(transcript_entries, 1):
            speaker = entry.get("speaker", "Interviewer")
            text = entry.get("text", "")
            body_html += f"<h3>Turn #{idx} - {speaker}</h3><p>{html.escape(text)}</p>"

        try:
            doc = QTextDocument()
            doc.setHtml(body_html)
            writer = QPdfWriter(str(pdf_path))
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            doc.print_(writer)
            return pdf_path
        except Exception as e:
            logger.error(f"Failed to export session PDF: {e}")
            return None

    def open_saved_folder(self):
        """Opens the saved interviews folder in Windows File Explorer."""
        try:
            os.startfile(str(self.output_dir))
        except Exception as e:
            logger.warning(f"Could not open folder: {e}")

    def _build_qa_html(self, question: str, answer: str, mode: str, provider: str) -> str:
        escaped_q = html.escape(question).replace("\n", "<br/>")

        # Convert markdown blocks in answer to HTML
        # Convert code blocks
        clean_ans = answer
        clean_ans = re.sub(
            r"```(?:\w+)?\n([\s\S]*?)```",
            lambda m: f"<pre style='background:#1e293b; color:#38bdf8; padding:10px; border-radius:6px; font-family:Consolas, monospace;'>{html.escape(m.group(1))}</pre>",
            clean_ans
        )
        # Bold
        clean_ans = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean_ans)
        # Markdown bullets
        clean_ans = re.sub(r"^\s*-\s+(.*)$", r"<li>\1</li>", clean_ans, flags=re.MULTILINE)
        clean_ans = re.sub(r"(<li>.*</li>)", r"<ul>\1</ul>", clean_ans, flags=re.DOTALL)
        clean_ans = clean_ans.replace("\n", "<br/>")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    color: #0f172a;
                    margin: 20px;
                    line-height: 1.6;
                }}
                .header {{
                    border-bottom: 2px solid #0284c7;
                    padding-bottom: 8px;
                    margin-bottom: 16px;
                }}
                .title {{
                    color: #0284c7;
                    font-size: 20px;
                    font-weight: bold;
                }}
                .meta {{
                    color: #64748b;
                    font-size: 11px;
                }}
                .badge {{
                    background-color: #e0f2fe;
                    color: #0369a1;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                    display: inline-block;
                }}
                .question-box {{
                    background-color: #f8fafc;
                    border-left: 4px solid #0284c7;
                    padding: 12px;
                    margin: 14px 0;
                    border-radius: 4px;
                }}
                .answer-box {{
                    margin-top: 14px;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <span class="title">ApexPilot AI &bull; Interview Record</span><br/>
                <span class="meta">Recorded on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} | Engine: {provider.upper()}</span>
                &nbsp;&nbsp;<span class="badge">{mode.upper()}</span>
            </div>
            
            <div class="question-box">
                <b>Question / Prompt:</b><br/>
                {escaped_q}
            </div>

            <div class="answer-box">
                <b>Solution & Talking Points:</b><br/>
                {clean_ans}
            </div>
        </body>
        </html>
        """


# Singleton instance
pdf_exporter = PDFExporter()
