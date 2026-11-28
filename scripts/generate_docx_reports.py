"""
Convert Markdown documentation to professional DOCX format with styling.
Generates DOCX versions of:
  - SAMARTH_WORK_W1_W2_DOCUMENTATION.md
  - OVERALL_CODE_ARCHITECTURE.md
  - WEEK2_REPORT.md
"""

import os
import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# Color Palette
NAVY_PRIMARY = RGBColor(27, 54, 93)     # #1B365D - Title / Main Headings
NAVY_SECONDARY = RGBColor(43, 87, 154)  # #2B579A - Subheadings
TEXT_DARK = RGBColor(36, 41, 47)        # #24292F - Body text
TEXT_MUTED = RGBColor(87, 96, 106)      # #57606A - Muted/captions
CODE_COLOR = RGBColor(176, 32, 55)      # #B02037 - Inline code
LINK_COLOR = RGBColor(9, 105, 218)      # #0969DA - Links

HEX_HEADER_BG = "2B579A"
HEX_ZEBRA_BG = "F7F9FB"
HEX_CODE_BG = "F6F8FA"
HEX_BORDER = "D0D7DE"


def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="D0D7DE", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_inline_runs(paragraph, text, base_font_size=10.5, is_italic=False, default_color=TEXT_DARK):
    pattern = re.compile(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))')
    parts = pattern.split(text)
    for part in parts:
        if not part:
            continue
        run = paragraph.add_run()
        run.font.name = 'Calibri'
        run.font.size = Pt(base_font_size)
        run.font.color.rgb = default_color
        
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run.text = part[2:-2]
            run.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
            run.text = part[1:-1]
            run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run.text = part[1:-1]
            run.font.name = 'Consolas'
            run.font.size = Pt(base_font_size - 1)
            run.font.color.rgb = CODE_COLOR
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
            if match:
                run.text = match.group(1)
                run.font.color.rgb = LINK_COLOR
                run.underline = True
            else:
                run.text = part
        else:
            run.text = part
            if is_italic:
                run.italic = True


def add_code_block(doc, code_lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    set_cell_background(cell, HEX_CODE_BG)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="2B579A"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    for i, line in enumerate(code_lines):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
        run = p.add_run(line)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.0)
        run.font.color.rgb = RGBColor(40, 44, 52)
    
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(6)


def add_callout_box(doc, text, alert_type="NOTE"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    
    color_map = {
        "NOTE": ("EBF3FB", "1F6FEB"),
        "TIP": ("EFF9F0", "2DA44E"),
        "IMPORTANT": ("F6F0FD", "8250DF"),
        "WARNING": ("FFF8E6", "BF8700"),
        "CAUTION": ("FFEBE9", "CF222E")
    }
    bg_color, border_color = color_map.get(alert_type.upper(), ("F6F8FA", "57606A"))
    
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="28" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run_badge = p.add_run(f"[{alert_type.upper()}] ")
    run_badge.bold = True
    run_badge.font.name = 'Calibri'
    run_badge.font.size = Pt(10)
    run_badge.font.color.rgb = RGBColor.from_string(border_color)
    add_inline_runs(p, text, base_font_size=10, default_color=TEXT_DARK)
    
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(6)


def add_table_data(doc, table_lines):
    rows_data = []
    for line in table_lines:
        line_clean = line.strip()
        if not line_clean.startswith("|"):
            continue
        # Split by | and strip
        parts = [c.strip() for c in line_clean.split("|")[1:-1]]
        # Check if separator row like |---|---|
        if all(re.match(r'^:?-+:?$', p) for p in parts if p):
            continue
        rows_data.append(parts)
    
    if not rows_data:
        return
    
    col_count = max(len(r) for r in rows_data)
    # Normalize row lengths
    for r in rows_data:
        while len(r) < col_count:
            r.append("")
    
    table = doc.add_table(rows=len(rows_data), cols=col_count)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table, color="D0D7DE", sz="4")
    
    for row_idx, r in enumerate(rows_data):
        row = table.rows[row_idx]
        is_header = (row_idx == 0)
        
        for col_idx, val in enumerate(r):
            cell = row.cells[col_idx]
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            
            if is_header:
                set_cell_background(cell, HEX_HEADER_BG)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                run = p.add_run(val)
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if row_idx % 2 == 1:
                    set_cell_background(cell, "FFFFFF")
                else:
                    set_cell_background(cell, HEX_ZEBRA_BG)
                
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                add_inline_runs(p, val, base_font_size=9.5, default_color=TEXT_DARK)
    
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(6)


def convert_md_to_docx(md_path: Path, docx_path: Path):
    print(f"Converting: {md_path.name} -> {docx_path.name}")
    content = md_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    
    doc = Document()
    
    # Page setup - Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
    
    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_lines = []
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Code block handler
        if stripped.startswith("```"):
            if in_code_block:
                add_code_block(doc, code_lines)
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Table handler
        if stripped.startswith("|"):
            table_lines.append(line)
            in_table = True
            i += 1
            continue
        else:
            if in_table:
                add_table_data(doc, table_lines)
                table_lines = []
                in_table = False
        
        # Blank line
        if not stripped:
            i += 1
            continue
        
        # Horizontal Rule
        if re.match(r'^(---+|\*\*\*+|___+)$', stripped):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="D0D7DE"/></w:pBdr>')
            p._p.get_or_add_pPr().append(pBdr)
            i += 1
            continue
        
        # Alert / Blockquote
        if stripped.startswith(">"):
            alert_match = re.match(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(.*)', stripped, re.IGNORECASE)
            if alert_match:
                alert_type = alert_match.group(1).upper()
                alert_text = alert_match.group(2)
                # Check for continuation lines
                i += 1
                while i < len(lines) and lines[i].strip().startswith(">"):
                    cont_line = re.sub(r'^>\s*', '', lines[i].strip())
                    if cont_line:
                        alert_text += " " + cont_line
                    i += 1
                add_callout_box(doc, alert_text, alert_type)
                continue
            else:
                # Normal blockquote
                quote_text = re.sub(r'^>\s*', '', stripped)
                i += 1
                while i < len(lines) and lines[i].strip().startswith(">"):
                    cont_line = re.sub(r'^>\s*', '', lines[i].strip())
                    if cont_line:
                        quote_text += " " + cont_line
                    i += 1
                add_callout_box(doc, quote_text, "NOTE")
                continue
        
        # Headings
        if stripped.startswith("#"):
            match = re.match(r'^(#{1,6})\s+(.*)', stripped)
            if match:
                level = len(match.group(1))
                heading_text = match.group(2).strip()
                p = doc.add_paragraph()
                
                if level == 1:
                    p.paragraph_format.space_before = Pt(16)
                    p.paragraph_format.space_after = Pt(6)
                    p.paragraph_format.keep_with_next = True
                    run = p.add_run(heading_text)
                    run.font.name = 'Calibri'
                    run.font.size = Pt(22)
                    run.bold = True
                    run.font.color.rgb = NAVY_PRIMARY
                    # Bottom underline accent
                    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="2B579A"/></w:pBdr>')
                    p._p.get_or_add_pPr().append(pBdr)
                elif level == 2:
                    p.paragraph_format.space_before = Pt(14)
                    p.paragraph_format.space_after = Pt(4)
                    p.paragraph_format.keep_with_next = True
                    run = p.add_run(heading_text)
                    run.font.name = 'Calibri'
                    run.font.size = Pt(15)
                    run.bold = True
                    run.font.color.rgb = NAVY_PRIMARY
                elif level == 3:
                    p.paragraph_format.space_before = Pt(10)
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.keep_with_next = True
                    run = p.add_run(heading_text)
                    run.font.name = 'Calibri'
                    run.font.size = Pt(12.5)
                    run.bold = True
                    run.font.color.rgb = NAVY_SECONDARY
                else:
                    p.paragraph_format.space_before = Pt(8)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.keep_with_next = True
                    run = p.add_run(heading_text)
                    run.font.name = 'Calibri'
                    run.font.size = Pt(11)
                    run.bold = True
                    run.font.color.rgb = TEXT_DARK
                
                i += 1
                continue
        
        # Bullet list
        bullet_match = re.match(r'^(\s*)[*\-+]\s+(.*)', line)
        if bullet_match:
            indent_spaces = len(bullet_match.group(1))
            bullet_text = bullet_match.group(2)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.left_indent = Inches(0.25 + (indent_spaces // 2) * 0.2)
            add_inline_runs(p, bullet_text, base_font_size=10.5)
            i += 1
            continue
        
        # Numbered list
        num_match = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if num_match:
            indent_spaces = len(num_match.group(1))
            num_text = num_match.group(2)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.left_indent = Inches(0.25 + (indent_spaces // 2) * 0.2)
            add_inline_runs(p, num_text, base_font_size=10.5)
            i += 1
            continue
        
        # Standard paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        add_inline_runs(p, stripped, base_font_size=10.5)
        i += 1
    
    # Process leftover table
    if in_table:
        add_table_data(doc, table_lines)
    
    # Save document
    doc.save(docx_path)
    print(f"Successfully generated: {docx_path} ({docx_path.stat().st_size} bytes)")


def main():
    workspace = Path(__file__).resolve().parent.parent
    targets = [
        ("SAMARTH_WORK_W1_W2_DOCUMENTATION.md", "SAMARTH_WORK_W1_W2_DOCUMENTATION.docx"),
        ("OVERALL_CODE_ARCHITECTURE.md", "OVERALL_CODE_ARCHITECTURE.docx"),
        ("WEEK2_REPORT.md", "WEEK2_REPORT.docx")
    ]
    
    generated = []
    for md_name, docx_name in targets:
        md_file = workspace / md_name
        docx_file = workspace / docx_name
        if md_file.exists():
            convert_md_to_docx(md_file, docx_file)
            generated.append(docx_file)
        else:
            print(f"Warning: {md_file} does not exist.")
    
    print("\nSummary of generated DOCX files:")
    for f in generated:
        print(f" - {f.name}: {f.stat().st_size / 1024:.1f} KB at {f}")

if __name__ == "__main__":
    main()
