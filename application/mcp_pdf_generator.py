import json
import logging
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("pdf-generator")

def generate_business_trip_pdf(content: str, destination: str) -> str:
    """
    Generate a business trip PDF based on the content and destination
    """
    try:
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"business_trip_{destination}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Build PDF content
        story = []
        
        # Title
        title = Paragraph(f"{destination} 출장 가이드", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Date
        date_text = f"생성일: {datetime.now().strftime('%Y년 %m월 %d일')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Parse content and create sections
        sections = content.split('\n\n')
        
        for section in sections:
            if section.strip():
                # Check if it's a heading (starts with #)
                if section.startswith('#'):
                    heading_text = section.replace('#', '').strip()
                    story.append(Paragraph(heading_text, heading_style))
                    story.append(Spacer(1, 12))
                else:
                    # Regular content
                    story.append(Paragraph(section.strip(), styles['Normal']))
                    story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        logger.info(f"PDF generated successfully: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return f"Error: {str(e)}"

def save_to_notion(content: str, destination: str) -> str:
    """
    Save business trip plan to Notion (placeholder for now)
    """
    try:
        # This is a placeholder - you would need to implement actual Notion API integration
        # For now, we'll create a JSON file that could be imported to Notion
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"notion_export_{destination}_{timestamp}.json"
        
        notion_data = {
            "title": f"{destination} 출장 가이드",
            "created_date": datetime.now().isoformat(),
            "destination": destination,
            "content": content,
            "type": "business_trip_plan"
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(notion_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Notion export file created: {filename}")
        return f"Notion 내보내기 파일이 생성되었습니다: {filename}"
        
    except Exception as e:
        logger.error(f"Error saving to Notion: {str(e)}")
        return f"Error: {str(e)}"