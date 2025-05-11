import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def generate_pdf(entity: str, content: str, news: list) -> str:
    try:
        font_name = "Helvetica"
        font_path = "DejaVuSans.ttf"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("DejaVu", font_path))
            font_name = "DejaVu"

        filename = f"{entity.replace(' ', '_')}_summary_{datetime.now().strftime('%Y%m%d')}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        left_margin = 40
        top_margin = height - 50
        bottom_margin = 40
        line_height = 14

        def draw_wrapped_lines(text_obj, lines):
            y = text_obj.getY()
            for line in lines:
                if y < bottom_margin:
                    c.drawText(text_obj)
                    c.showPage()
                    text_obj = c.beginText(left_margin, top_margin)
                    text_obj.setFont(font_name, 11)
                    y = text_obj.getY()
                text_obj.textLine(line)
                y -= line_height
            return text_obj

        def wrap_line(line, width_limit=100):
            words = line.split()
            wrapped = []
            current = []
            for word in words:
                if len(' '.join(current + [word])) < width_limit:
                    current.append(word)
                else:
                    wrapped.append(' '.join(current))
                    current = [word]
            if current:
                wrapped.append(' '.join(current))
            return wrapped

        c.setFont(font_name, 16)
        c.drawCentredString(width / 2, top_margin, f"Summary of {entity}")

        c.setFont(font_name, 11)
        text = c.beginText(left_margin, top_margin - 40)

        content_lines = []
        for line in content.split("\n"):
            if line.strip():
                content_lines.extend(wrap_line(line))

        text = draw_wrapped_lines(text, content_lines)

        if news:
            text.textLine("")
            text.textLine("Official News:")
            for item in news:
                text = draw_wrapped_lines(text, wrap_line(f"- {item.get('title', 'No title')}"))
                text = draw_wrapped_lines(text, wrap_line(f"  {item.get('link', 'No link')}"))

        c.drawText(text)
        c.save()
        return filename
    except Exception as e:
        return ""
