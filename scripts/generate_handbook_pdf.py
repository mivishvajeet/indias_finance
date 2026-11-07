import re
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header
        self.drawString(54, letter[1] - 36, "🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL — TECHNICAL HANDBOOK")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_str)
        self.drawString(54, 30, "CONFIDENTIAL & PROPRIETARY — DATA PLATFORM ARCHITECTURE")
        self.line(54, 42, letter[0] - 54, 42)
        self.restoreState()

def build_pdf(md_path: Path, pdf_path: Path):
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    c_primary = colors.HexColor("#0F172A")
    c_accent = colors.HexColor("#0284C7")
    c_text = colors.HexColor("#334155")
    c_code_bg = colors.HexColor("#F8FAFC")
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        alignment=1, # Center
        spaceAfter=12
    )
    
    sub_style = ParagraphStyle(
        'CoverSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=24
    )
    
    h1_style = ParagraphStyle(
        'H1Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h3_style = ParagraphStyle(
        'H3Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=6
    )
    
    quote_style = ParagraphStyle(
        'QuoteStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0369A1"),
        leftIndent=15,
        spaceBefore=4,
        spaceAfter=6
    )
    
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0F172A")
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B")
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []
    
    # Cover Page
    story.append(Spacer(1, 40))
    story.append(Paragraph("🇮🇳 INDIA FINANCE INTELLIGENCE TERMINAL", title_style))
    story.append(Paragraph("Master Technical Handbook & Complete Engineering Guide", sub_style))
    story.append(HRFlowable(width="80%", thickness=2, color=c_accent, spaceBefore=0, spaceAfter=20))
    
    meta_text = """
    <b>Domain:</b> Institutional Financial Research & Medallion Lakehouse<br/>
    <b>Technology Stack:</b> Python 3.12, DuckDB, dbt-duckdb, Apache Parquet, Streamlit<br/>
    <b>Target Market:</b> National Stock Exchange (NSE), AMFI Mutual Funds, RBI/MOSPI Macro<br/>
    <b>Verification:</b> 112/112 Automated Tests Passing (100.0% Verified Data Quality Scorecard)<br/>
    <b>Author / Architect:</b> Vishvajeet (Data Engineering & Financial Systems)<br/>
    <b>Repository:</b> github.com/mivishvajeet/indias_finance
    """
    story.append(Paragraph(meta_text, ParagraphStyle('CoverMeta', parent=body_style, fontSize=9.5, leading=15, alignment=1)))
    story.append(Spacer(1, 40))
    story.append(PageBreak())
    
    # Read and parse Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []
    
    for line in lines:
        stripped = line.strip()
        
        # Code block handling
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                code_text = "<br/>".join(code_lines).replace(" ", "&nbsp;")
                p_code = Paragraph(code_text, code_style)
                t_code = Table([[p_code]], colWidths=[500])
                t_code.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), c_code_bg),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(t_code)
                story.append(Spacer(1, 6))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue
            
        if in_code_block:
            safe_l = line.rstrip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_lines.append(safe_l)
            continue
            
        # Table handling
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(re.match(r'^:?-+:?$', c) for c in cells):
                continue  # Divider line
            in_table = True
            table_rows.append(cells)
            continue
        elif in_table:
            # End of table
            in_table = False
            if table_rows:
                num_cols = len(table_rows[0])
                col_w = 504 / num_cols
                formatted_table_data = []
                for r_idx, r in enumerate(table_rows):
                    row_cells = []
                    for c_idx, cell_val in enumerate(r):
                        # clean markdown bold
                        c_clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', cell_val)
                        if r_idx == 0:
                            row_cells.append(Paragraph(c_clean, table_header_style))
                        else:
                            row_cells.append(Paragraph(c_clean, table_cell_style))
                    formatted_table_data.append(row_cells)
                
                t = Table(formatted_table_data, colWidths=[col_w] * num_cols)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F172A")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
            table_rows = []
            
        if not stripped:
            continue
            
        # Headers
        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            story.append(Paragraph(h_text, h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceBefore=2, spaceAfter=8))
        elif stripped.startswith("### "):
            h_text = stripped[4:].strip()
            story.append(Paragraph(h_text, h2_style))
        elif stripped.startswith("#### "):
            h_text = stripped[5:].strip()
            story.append(Paragraph(h_text, h3_style))
        elif stripped.startswith("> "):
            q_text = stripped[2:].strip()
            q_clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', q_text)
            q_clean = re.sub(r'\*(.*?)\*', r'<i>\1</i>', q_clean)
            story.append(Paragraph(q_clean, quote_style))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            b_text = "&bull; " + stripped[2:].strip()
            b_clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', b_text)
            b_clean = re.sub(r'\*(.*?)\*', r'<i>\1</i>', b_clean)
            b_clean = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', b_clean)
            story.append(Paragraph(b_clean, body_style))
        else:
            p_clean = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', stripped)
            p_clean = re.sub(r'\*(.*?)\*', r'<i>\1</i>', p_clean)
            p_clean = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', p_clean)
            story.append(Paragraph(p_clean, body_style))
            
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {pdf_path} ({pdf_path.stat().st_size:,} bytes)")

if __name__ == "__main__":
    md_file = Path("docs/PROJECT_TECHNICAL_HANDBOOK.md")
    pdf_file = Path("docs/PROJECT_TECHNICAL_HANDBOOK.pdf")
    build_pdf(md_file, pdf_file)
