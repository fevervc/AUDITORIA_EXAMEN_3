import markdown
import re
from fpdf import FPDF

class AuditPDF(FPDF):
    def header(self):
        # Page header
        self.set_font('helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'INFORME FINAL DE AUDITORIA DE SISTEMAS - CORPORATE EPIS PILOT', align='L', new_x="RIGHT", new_y="TOP")
        self.ln(8)
        self.set_draw_color(200, 200, 200)
        self.line(10, 16, 200, 16)
        self.ln(4)

    def footer(self):
        # Page footer
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Pagina {self.page_no()}/{{nb}}', align='R')
        self.set_y(-15)
        self.cell(0, 10, 'Curso de Auditoria de TI - EPIS 2026', align='L')

def sanitize_text(text):
    # Map common emojis/symbols to latin-1 equivalents
    replacements = {
        "🔗": "Link: ",
        "🔴": "[ALTO] ",
        "🟡": "[MEDIO] ",
        "🟢": "[BAJO] ",
        "✅": "[OK] ",
        "⏳": "[PENDIENTE] ",
        "⚠️": "[ADVERTENCIA] ",
        "🐳": "[Docker] ",
        "🤖": "[IA] ",
        "🎫": "[Ticket] ",
        "📋": "[Reporte] ",
        "📁": "[Carpeta] ",
        "🚀": "[Push] ",
        "→": "->",
        "➤": ">",
        "•": "*",
        "°": "o",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "--",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Remove any other non-latin-1 characters
    sanitized = ""
    for char in text:
        try:
            char.encode("latin-1")
            sanitized += char
        except UnicodeEncodeError:
            pass
    return sanitized

def sanitize_td_tags(html):
    # Regex to strip tags inside td/th elements as fpdf2 doesn't support nested tags inside cells
    def clean_td(match):
        content = match.group(1)
        cleaned = re.sub(r'<[^>]+>', '', content)
        return f"<td>{cleaned}</td>"
    
    def clean_th(match):
        content = match.group(1)
        cleaned = re.sub(r'<[^>]+>', '', content)
        return f"<th>{cleaned}</th>"

    html = re.sub(r'<td>(.*?)</td>', clean_td, html, flags=re.DOTALL)
    html = re.sub(r'<th>(.*?)</th>', clean_th, html, flags=re.DOTALL)
    return html

def sanitize_anchor_links(html):
    # Convert <a href="#...">text</a> to text to prevent named destination exceptions in fpdf2
    def strip_internal_links(match):
        return match.group(1)
    
    html = re.sub(r'<a\s+href="#[^"]*">(.*?)</a>', strip_internal_links, html, flags=re.DOTALL)
    html = re.sub(r"<a\s+href='#[^']*'>(.*?)</a>", strip_internal_links, html, flags=re.DOTALL)
    return html

def main():
    # Read README.md
    with open("README.md", "r", encoding="utf-8") as f:
        md_content = f.read()

    # Sanitize markdown content
    sanitized_md = sanitize_text(md_content)

    # Convert to HTML
    html_content = markdown.markdown(sanitized_md, extensions=['tables', 'fenced_code'])

    # Sanitize td/th elements
    html_content = sanitize_td_tags(html_content)

    # Sanitize anchor links
    html_content = sanitize_anchor_links(html_content)

    # Wrap in basic HTML structure
    full_html = f"""
    <html>
    <head>
    <style>
      body {{ font-family: helvetica; font-size: 10pt; color: #333333; }}
      h1 {{ font-family: helvetica; font-size: 18pt; font-weight: bold; color: #1a365d; margin-top: 15px; margin-bottom: 10px; }}
      h2 {{ font-family: helvetica; font-size: 14pt; font-weight: bold; color: #2c5282; margin-top: 12px; margin-bottom: 8px; }}
      h3 {{ font-family: helvetica; font-size: 11pt; font-weight: bold; color: #4a5568; margin-top: 10px; margin-bottom: 6px; }}
      p {{ margin-bottom: 8px; line-height: 1.4; }}
      ul {{ margin-bottom: 8px; }}
      li {{ margin-bottom: 4px; }}
      table {{ border-collapse: collapse; width: 100%; margin-top: 10px; margin-bottom: 10px; }}
      th {{ background-color: #ebf8ff; color: #2b6cb0; font-weight: bold; border: 1px solid #cbd5e0; padding: 6px; }}
      td {{ border: 1px solid #cbd5e0; padding: 6px; }}
      code {{ font-family: courier; font-size: 9pt; background-color: #f7fafc; }}
      blockquote {{ border-left: 3px solid #cbd5e0; padding-left: 10px; color: #4a5568; margin-left: 10px; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    # Generate PDF
    pdf = AuditPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("helvetica", size=10)
    pdf.write_html(full_html)
    pdf.output("Informe_Auditoria.pdf")
    print("PDF generated successfully!")

if __name__ == "__main__":
    main()
