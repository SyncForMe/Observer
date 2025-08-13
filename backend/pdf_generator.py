"""
Professional PDF Generation System for AI Agent Simulation Platform
Converts documents to beautifully formatted PDF files with proper styling.
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from io import BytesIO
from datetime import datetime
import os
import base64
import logging
import tempfile
from pathlib import Path

class ProfessionalPDFGenerator:
    """Generate professional PDF documents with proper formatting, headers, and styling"""
    
    def __init__(self):
        self.font_config = FontConfiguration()
        self.setup_css()
    
    def setup_css(self):
        """Setup professional CSS styling for PDF documents"""
        self.base_css = """
        @page {
            size: A4;
            margin: 2cm 2.5cm 3cm 2.5cm;
            @top-center {
                content: "AI Agent Simulation Platform";
                font-size: 10pt;
                color: #666;
                border-bottom: 1px solid #ddd;
                padding-bottom: 5pt;
            }
            @bottom-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        h1 {
            color: #1a365d;
            font-size: 24pt;
            font-weight: bold;
            margin: 0 0 20pt 0;
            padding: 15pt 0;
            border-bottom: 3px solid #3182ce;
            text-align: center;
        }
        
        h2 {
            color: #2d3748;
            font-size: 18pt;
            font-weight: bold;
            margin: 25pt 0 12pt 0;
            padding: 8pt 0 4pt 0;
            border-bottom: 2px solid #e2e8f0;
        }
        
        h3 {
            color: #4a5568;
            font-size: 14pt;
            font-weight: bold;
            margin: 20pt 0 10pt 0;
        }
        
        h4 {
            color: #718096;
            font-size: 12pt;
            font-weight: bold;
            margin: 15pt 0 8pt 0;
        }
        
        p {
            margin: 0 0 12pt 0;
            text-align: justify;
        }
        
        ul, ol {
            margin: 12pt 0;
            padding-left: 25pt;
        }
        
        li {
            margin: 6pt 0;
        }
        
        .document-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25pt;
            margin: -20pt -20pt 25pt -20pt;
            text-align: center;
        }
        
        .document-meta {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            padding: 15pt;
            margin: 0 0 25pt 0;
            font-size: 10pt;
        }
        
        .authors {
            font-weight: bold;
            color: #2d3748;
        }
        
        .created-date {
            color: #718096;
            font-style: italic;
        }
        
        .category {
            background: #3182ce;
            color: white;
            padding: 3pt 8pt;
            border-radius: 4pt;
            font-size: 9pt;
            font-weight: bold;
        }
        
        .keywords {
            color: #4a5568;
            font-size: 9pt;
        }
        
        blockquote {
            border-left: 4px solid #3182ce;
            margin: 15pt 0;
            padding: 10pt 20pt;
            background: #f7fafc;
            font-style: italic;
        }
        
        .highlight {
            background: #fed7e2;
            padding: 2pt 4pt;
            font-weight: bold;
        }
        
        .warning {
            background: #fef5e7;
            border: 1px solid #f6ad55;
            padding: 12pt;
            margin: 15pt 0;
            border-radius: 4pt;
        }
        
        .success {
            background: #f0fff4;
            border: 1px solid #68d391;
            padding: 12pt;
            margin: 15pt 0;
            border-radius: 4pt;
        }
        
        .info {
            background: #ebf8ff;
            border: 1px solid #63b3ed;
            padding: 12pt;
            margin: 15pt 0;
            border-radius: 4pt;
        }
        
        code {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            padding: 2pt 4pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 15pt;
            margin: 15pt 0;
            border-radius: 4pt;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
            overflow: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
        }
        
        th, td {
            border: 1px solid #e2e8f0;
            padding: 8pt 12pt;
            text-align: left;
        }
        
        th {
            background: #f7fafc;
            font-weight: bold;
            color: #2d3748;
        }
        
        .footer-note {
            margin-top: 40pt;
            padding-top: 15pt;
            border-top: 1px solid #e2e8f0;
            font-size: 9pt;
            color: #718096;
            text-align: center;
        }
        """
    
    def convert_markdown_to_html(self, content: str, title: str = "", authors: list = None, 
                                category: str = "", description: str = "", keywords: list = None,
                                created_at: str = None) -> str:
        """Convert markdown content to professional HTML with metadata"""
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'toc', 'tables'])
        html_content = md.convert(content)
        
        # Prepare metadata
        authors_str = ", ".join(authors) if authors else "AI Agent System"
        created_date = created_at or datetime.now().strftime("%B %d, %Y")
        keywords_str = ", ".join(keywords) if keywords else ""
        
        # Build complete HTML document
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body>
            <div class="document-header">
                <h1>{title}</h1>
            </div>
            
            <div class="document-meta">
                <div class="authors"><strong>Created by:</strong> {authors_str}</div>
                <div class="created-date"><strong>Date:</strong> {created_date}</div>
                <div style="margin: 8pt 0;">
                    <span class="category">{category.upper()}</span>
                </div>
                {f'<div class="keywords"><strong>Keywords:</strong> {keywords_str}</div>' if keywords_str else ''}
                {f'<div style="margin-top: 8pt; font-style: italic;">{description}</div>' if description else ''}
            </div>
            
            <div class="content">
                {html_content}
            </div>
            
            <div class="footer-note">
                Generated by AI Agent Simulation Platform • {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def generate_pdf(self, content: str, title: str = "Document", authors: list = None,
                    category: str = "General", description: str = "", keywords: list = None,
                    created_at: str = None) -> bytes:
        """Generate PDF from content with professional formatting"""
        
        try:
            # Convert content to HTML
            html_content = self.convert_markdown_to_html(
                content=content,
                title=title,
                authors=authors,
                category=category,
                description=description,
                keywords=keywords,
                created_at=created_at
            )
            
            # Create PDF
            pdf_buffer = BytesIO()
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=self.base_css, font_config=self.font_config)
            
            html_doc.write_pdf(pdf_buffer, stylesheets=[css_doc], font_config=self.font_config)
            
            pdf_buffer.seek(0)
            pdf_bytes = pdf_buffer.getvalue()
            
            logging.info(f"✅ Generated PDF: {title} ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logging.error(f"❌ PDF generation failed: {e}")
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def generate_pdf_base64(self, content: str, title: str = "Document", authors: list = None,
                           category: str = "General", description: str = "", keywords: list = None,
                           created_at: str = None) -> str:
        """Generate PDF and return as base64 string for easy storage/transmission"""
        
        pdf_bytes = self.generate_pdf(
            content=content,
            title=title,
            authors=authors,
            category=category,
            description=description,
            keywords=keywords,
            created_at=created_at
        )
        
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
    def save_pdf_file(self, content: str, output_path: str, title: str = "Document", 
                     authors: list = None, category: str = "General", description: str = "",
                     keywords: list = None, created_at: str = None):
        """Generate and save PDF to file"""
        
        pdf_bytes = self.generate_pdf(
            content=content,
            title=title,
            authors=authors,
            category=category,
            description=description,
            keywords=keywords,
            created_at=created_at
        )
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        logging.info(f"✅ PDF saved to: {output_path}")

# Utility function for easy usage
def generate_document_pdf(document_data: dict) -> bytes:
    """
    Generate PDF from document data dictionary
    
    Expected format:
    {
        'content': 'Document content in markdown',
        'title': 'Document Title',
        'authors': ['Author 1', 'Author 2'],
        'category': 'Protocol',
        'description': 'Document description',
        'keywords': ['keyword1', 'keyword2'],
        'created_at': '2024-01-01'
    }
    """
    generator = ProfessionalPDFGenerator()
    
    return generator.generate_pdf(
        content=document_data.get('content', ''),
        title=document_data.get('title', 'Untitled Document'),
        authors=document_data.get('authors', []),
        category=document_data.get('category', 'General'),
        description=document_data.get('description', ''),
        keywords=document_data.get('keywords', []),
        created_at=document_data.get('created_at')
    )

def generate_pdf_from_html(html_content: str) -> bytes:
    """
    Generate PDF directly from HTML content
    
    This function is used by the report PDF download endpoint
    to convert HTML reports to PDF format.
    """
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        from io import BytesIO
        
        # Create font configuration
        font_config = FontConfiguration()
        
        # Basic CSS for HTML to PDF conversion
        basic_css = """
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 20px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .meta {
            color: #666;
            font-size: 14px;
        }
        .section {
            margin-bottom: 25px;
            padding: 20px;
            border-left: 4px solid #3b82f6;
            background: #f8fafc;
        }
        .section-header {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #1f2937;
        }
        .section-content {
            line-height: 1.6;
        }
        strong {
            color: #1f2937;
        }
        """
        
        # Create PDF
        pdf_buffer = BytesIO()
        html_doc = HTML(string=html_content)
        css_doc = CSS(string=basic_css, font_config=font_config)
        
        html_doc.write_pdf(pdf_buffer, stylesheets=[css_doc], font_config=font_config)
        
        pdf_buffer.seek(0)
        pdf_bytes = pdf_buffer.getvalue()
        
        logging.info(f"✅ Generated PDF from HTML: {len(pdf_bytes)} bytes")
        return pdf_bytes
        
    except Exception as e:
        logging.error(f"❌ PDF generation from HTML failed: {e}")
        raise Exception(f"PDF generation from HTML failed: {str(e)}")

# Test function
if __name__ == "__main__":
    # Test PDF generation
    test_content = """
# Test Document

## Introduction
This is a **test document** to verify PDF generation capabilities.

### Key Features
- Professional formatting
- Proper headers and styling
- Support for *italics* and **bold** text
- Tables and lists

### Sample Table
| Feature | Status | Notes |
|---------|--------|-------|
| PDF Generation | ✅ Working | High quality output |
| Markdown Support | ✅ Working | Full feature set |
| Professional Styling | ✅ Working | Beautiful design |

## Conclusion
The PDF generation system is working correctly!
    """
    
    generator = ProfessionalPDFGenerator()
    pdf_bytes = generator.generate_pdf(
        content=test_content,
        title="Test Document",
        authors=["AI System"],
        category="Test",
        description="Testing PDF generation capabilities",
        keywords=["test", "pdf", "document"]
    )
    
    print(f"Generated test PDF: {len(pdf_bytes)} bytes")