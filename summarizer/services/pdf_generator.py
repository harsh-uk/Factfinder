import os
from datetime import datetime

import PyPDF2
import markdown
import pdfkit
from jinja2 import Environment

config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
def generate_pdf(entity, summary, news, metrics):
    # Format entity name and create filenames
    entity_title = " ".join(word.capitalize() for word in entity.split())
    base_filename = f"{entity.replace(' ', '_')}_summary_{datetime.now().strftime('%Y%m%d')}"
    summary_dir = "summaries"
    temp_dir = os.path.join(summary_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    temp_html = os.path.join(temp_dir, f"temp_{base_filename}.html")
    output_pdf = os.path.join(temp_dir, f"{base_filename}.pdf")
    final_pdf = os.path.join(summary_dir, f"{base_filename}_final.pdf")


    # Convert markdown to HTML
    html_content = markdown.markdown(summary, extensions=['tables', 'fenced_code'])

    # Create HTML using Jinja2 template string
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ entity_title }} - Company Summary</title>
        <style>
            @page {
                size: letter portrait;
                margin: 2cm;
            }
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 21cm;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 30px;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
            h2 {
                color: #2c3e50;
                font-size: 18px;
                margin-top: 25px;
                border-bottom: 1px solid #eee;
                padding-bottom: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 12px;
            }
            ul {
                padding-left: 20px;
            }
            li {
                margin-bottom: 8px;
            }
            .metrics-table th {
                width: 40%;
            }
            .news-item {
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 1px solid #eee;
            }
            .news-title {
                font-weight: bold;
                font-size: 16px;
            }
            .news-link {
                font-size: 14px;
                color: #3498db;
            }
            .footer {
                text-align: center;
                font-size: 10px;
                color: #777;
                margin-top: 30px;
                border-top: 1px solid #eee;
                padding-top: 10px;
            }
        </style>
    </head>
    <body>
        <h1>{{ entity_title }} - Company Summary Report</h1>
        
        <h2>Company Overview</h2>
        <div class="overview-content">
            {{ html_content|safe }}
        </div>
        
        {% if metrics %}
        <h2>Key Financial Metrics</h2>
        <table class="metrics-table">
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            {% for key, value in metrics.items() %}
            <tr>
                <td>{{ key }}</td>
                <td>{{ value }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
        
        {% if news %}
        <h2>Latest News</h2>
        {% for item in news %}
        <div class="news-item">
            <div class="news-title">{{ item.title }}</div>
            {% if item.link %}
            <div class="news-link"><a href="{{ item.link }}">{{ item.link }}</a></div>
            {% endif %}
        </div>
        {% endfor %}
        {% endif %}
        
        <div class="footer">
            Generated on {{ today }} | {{ entity_title }} Company Report
        </div>
    </body>
    </html>
    """
    def format_metric(v):
        try:
            v = float(v)
            if v >= 1e9:
                return f"{v / 1e9:.2f}B USD"
            elif v >= 1e6:
                return f"{v / 1e6:.2f}M USD"
            elif v >= 1e3:
                return f"{v / 1e3:.2f}K USD"
            else:
                return f"{v:.2f}"
        except:
            return str(v)

    formatted_metrics = {k: format_metric(v) for k, v in (metrics or {}).items()}
    # Create Jinja2 environment and render template
    env = Environment()
    template = env.from_string(template_str)
    rendered_html = template.render(
        entity_title=entity_title,
        html_content=html_content,
        metrics=formatted_metrics,
        news=news or [],
        today=datetime.now().strftime("%B %d, %Y")
    )

    # Save HTML file temporarily
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(rendered_html)

    # Configure PDF options
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None,
        'quiet': '',
    }

    # Convert HTML to PDF using pdfkit
    try:
        pdfkit.from_file(temp_html, output_pdf, options=options,configuration=config)
    except Exception as e:
        print(f"Error generating PDF with pdfkit: {e}")
        # If pdfkit fails, we can try an alternative like WeasyPrint
        try:
            from weasyprint import HTML
            HTML(temp_html).write_pdf(output_pdf)
        except Exception as e2:
            print(f"Alternative PDF generation failed: {e2}")
            return None

    # Use PyPDF2 to add any additional processing if needed
    # (like adding headers, footers, or merging with templates)
    try:
        # Read the generated PDF
        reader = PyPDF2.PdfReader(output_pdf)
        writer = PyPDF2.PdfWriter()

        # Process each page (here we're just copying them as-is,
        # but you could modify them if needed)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            writer.add_page(page)

        # Add metadata
        writer.add_metadata({
            "/Title": f"{entity_title} Company Summary Report",
            "/Author": "Report Generator",
            "/CreationDate": datetime.now().strftime("D:%Y%m%d%H%M%S"),
            "/Producer": "PyPDF2"
        })

        # Save the final PDF
        with open(final_pdf, "wb") as output_file:
            writer.write(output_file)

        # Clean up temporary files
        try:
            os.remove(temp_html)
            os.remove(output_pdf)
        except Exception as cleanup_error:
            print(f"Cleanup failed: {cleanup_error}")


        return final_pdf

    except Exception as e:
        print(f"Error in PyPDF2 processing: {e}")
        # Return the original PDF if PyPDF2 processing fails
        if os.path.exists(output_pdf):
            return output_pdf
        return None
