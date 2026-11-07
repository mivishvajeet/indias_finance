import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

out_path = Path("docs/India_Finance_Intelligence_Presentation.pptx")
print(f"Generating editable PPTX presentation at {out_path}...")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6] # completely blank slide

# Design Tokens
C_BG_DARK = RGBColor(8, 12, 18)
C_PANEL = RGBColor(17, 26, 38)
C_BORDER = RGBColor(37, 51, 70)
C_TEXT_PRIMARY = RGBColor(230, 237, 245)
C_TEXT_SECONDARY = RGBColor(145, 160, 179)
C_GREEN = RGBColor(0, 192, 135)
C_BLUE = RGBColor(69, 163, 255)
C_YELLOW = RGBColor(245, 185, 66)
C_RED = RGBColor(255, 92, 101)

def apply_background(slide):
    bg_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = C_BG_DARK
    bg_shape.line.fill.background()
    return bg_shape

def add_header(slide, badge_text, title_text, subtitle_text):
    # Badge
    tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
    tf = tx_box.text_frame
    tf.word_wrap = True
    p_badge = tf.paragraphs[0]
    p_badge.text = badge_text.upper()
    p_badge.font.name = "Courier New"
    p_badge.font.size = Pt(11)
    p_badge.font.bold = True
    p_badge.font.color.rgb = C_BLUE

    # Title
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = "Arial"
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = C_TEXT_PRIMARY
    p_title.space_after = Pt(2)

    # Subtitle
    p_sub = tf.add_paragraph()
    p_sub.text = subtitle_text
    p_sub.font.name = "Arial"
    p_sub.font.size = Pt(12)
    p_sub.font.color.rgb = C_TEXT_SECONDARY

def add_card(slide, left, top, width, height, title, items, border_color=C_BORDER):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = C_PANEL
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)

    tf = card.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.3)
    tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.3)
    tf.margin_bottom = Inches(0.3)

    p_title = tf.paragraphs[0]
    p_title.text = title
    p_title.font.name = "Arial"
    p_title.font.size = Pt(15)
    p_title.font.bold = True
    p_title.font.color.rgb = C_TEXT_PRIMARY
    p_title.space_after = Pt(10)

    for item in items:
        p_item = tf.add_paragraph()
        p_item.text = f"• {item}"
        p_item.font.name = "Arial"
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = C_TEXT_SECONDARY
        p_item.space_after = Pt(6)

def set_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text

# Import slide definitions from build_presentation_html
from build_presentation_html import slides

for s in slides:
    slide = prs.slides.add_slide(blank_layout)
    apply_background(slide)
    add_header(slide, s["badge"], s["title"], s["subtitle"])
    set_notes(slide, s["notes"])

    # Slide-specific content formatting
    s_id = s["id"]
    if s_id == 1 or s_id == 30:
        # Hero Slide
        hero_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(4.5))
        tf = hero_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = "112 / 112 AUTOMATED TESTS PASSING  •  100.0% VERIFIED DATA QUALITY"
        p.alignment = PP_ALIGN.CENTER
        p.font.name = "Courier New"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = C_GREEN
        p.space_after = Pt(16)

        p2 = tf.add_paragraph()
        p2.text = "An institutional-grade Medallion Lakehouse platform for NSE Equities, AMFI Mutual Funds, and RBI/MOSPI Macroeconomic Indicators engineered with automated circuit breakers, zero lock contention, and safe local AI."
        p2.alignment = PP_ALIGN.CENTER
        p2.font.name = "Arial"
        p2.font.size = Pt(16)
        p2.font.color.rgb = C_TEXT_SECONDARY
        p2.space_after = Pt(24)

        p3 = tf.add_paragraph()
        p3.text = "DuckDB (In-Process OLAP)  |  dbt-duckdb  |  Apache Parquet  |  Python 3.12  |  Streamlit  |  Pytest  |  Local Safe Text-to-SQL"
        p3.alignment = PP_ALIGN.CENTER
        p3.font.name = "Courier New"
        p3.font.size = Pt(12)
        p3.font.color.rgb = C_BLUE

    elif s_id == 2:
        # 3 Pillar Cards
        add_card(slide, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "1. Financial Intelligence", [
            "Nifty 50 constituents & benchmarks",
            "Multi-factor screener (RSI, SMA, MACD)",
            "AMFI mutual fund NAV tracking",
            "RBI repo rate & MOSPI inflation",
            "Sharpe & Sortino vs 6.5% G-Sec"
        ], C_GREEN)
        add_card(slide, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "2. Data Observability", [
            "Bronze Hive-partitioned Parquet",
            "SHA-256 batch manifest idempotency",
            "Silver deduplication on natural keys",
            "NSE trading calendar validation",
            "112 automated tests & lineage DAG"
        ], C_BLUE)
        add_card(slide, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "3. Safe Local AI", [
            "Local deterministic text-to-SQL",
            "AST-based SELECT-only safety",
            "Zero mutating queries (DROP/DELETE)",
            "Execution against read-only DuckDB",
            "Exact SQL & data provenance citations"
        ], C_YELLOW)

    elif s_id == 7:
        # Medallion 3 tiers
        add_card(slide, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.8), "BRONZE LAYER (163 rows)", [
            "Format: Apache Parquet (Snappy)",
            "Hive Partitioning: year/month/day",
            "SHA-256 batch cryptographic manifests",
            "Immutable append-only raw storage",
            "Preserves raw ticks for auditability"
        ], C_BLUE)
        add_card(slide, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.8), "SILVER LAYER (133 rows)", [
            "Engine: DuckDB in-process views",
            "Deduplication: natural keys (symbol, date)",
            "Eliminated 30 duplicate raw ticks",
            "Calendar: NSE official holiday audit",
            "Clamps: close > 0, nav > 0, high >= low"
        ], C_YELLOW)
        add_card(slide, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.8), "GOLD LAYER (133 rows)", [
            "Modeling: Ralph Kimball star schema",
            "Calendar: Indian FY (April to March)",
            "SQL Technicals: RSI 14, Bollinger, MACD",
            "Risk Engine: CAGR, Sharpe, Sortino",
            "100.0% retention rate from Silver"
        ], C_GREEN)

    elif s_id == 16:
        # Waterfall
        add_card(slide, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Physical Record Waterfall", [
            "Bronze Raw Lakehouse: 163 records",
            "Deduplication Delta: -30 duplicate ticks",
            "Silver Staging Views: 133 conformed rows",
            "Transformation Delta: 0 unexplained dropouts",
            "Gold Fact Yield: 133 certified fact rows",
            "Retention Rate: 100.0% Verified"
        ], C_GREEN)
        add_card(slide, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8), "Mathematical Reconciliation", [
            "Audited by LakehouseReconciliationAuditor",
            "Natural key surrogate: SHA256(symbol + date)",
            "Guarantees that duplicate ingestion never bloats facts",
            "Singular dbt test: test_reconcile_staging_fact_rows",
            "Continuous verification on every pipeline execution"
        ], C_BLUE)

    elif s_id in [18, 19, 20, 22]:
        # Screenshots
        img_map = {
            18: "assets/page_1_market_intelligence_rendered_1794054266869.png",
            19: "assets/page_2_mutual_fund_risk_engine_1794054287354.png",
            20: "assets/page_4_macroeconomic_indicators_1794054304336.png",
            22: "assets/page_3_data_quality_center_1794054341660.png"
        }
        img_path = Path("docs") / img_map[s_id]
        if img_path.exists():
            slide.shapes.add_picture(str(img_path), Inches(0.8), Inches(2.0), width=Inches(7.2))
        
        # Side summary card
        add_card(slide, Inches(8.3), Inches(2.0), Inches(4.2), Inches(4.8), "Workspace Capabilities", [
            "Interactive Plotly subplots & filters",
            "Tabular typography (JetBrains Mono)",
            "Real-time benchmark quotes & gauges",
            "Tested against actual DuckDB marts",
            "Zero client-side calculation lag"
        ], C_BLUE)

    else:
        # Default 2-column or 3-column card breakdown
        add_card(slide, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.8), "Technical Architecture & Implementation", [
            "Engineered in modular Python & dbt SQL",
            "Validated against official Indian exchange standards",
            "Complete regression protection via automated tests",
            "Transparent metadata and data provenance",
            "Direct traceability from raw files to UI components"
        ], C_BLUE)
        add_card(slide, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.8), "Key Engineering Highlights", [
            "Zero cloud cost in-process execution",
            "Mathematical idempotency via SHA-256 manifests",
            "Decoupled read-only analytical connection pool",
            "AST-level security guardrails for AI assistance",
            "100% verified data quality scorecard"
        ], C_GREEN)

prs.save(str(out_path))
print(f"Successfully generated editable presentation PPTX at {out_path} ({out_path.stat().st_size:,} bytes)!")
