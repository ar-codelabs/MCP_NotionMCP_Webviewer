"""
출장 계획서 PDF 생성을 위한 MCP 서버
"""
from mcp.server.fastmcp import FastMCP
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
import json

mcp = FastMCP(
    name="pdf-generator",
    instructions="출장 계획서 PDF 생성을 담당합니다."
)

@mcp.tool()
def generate_business_trip_pdf(
    destination: str,
    start_date: str = "",
    end_date: str = "",
    purpose: str = "업무 출장",
    traveler_name: str = "출장자",
    department: str = "부서명",
    position: str = "직급",
    accommodation: str = "미정",
    transportation: str = "항공",
    estimated_cost: str = "미정"
) -> str:
    """
    출장 계획서 PDF를 생성합니다.
    
    Args:
        destination: 출장지
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        purpose: 출장 목적
        traveler_name: 출장자 이름
        department: 부서
        position: 직급
        accommodation: 숙박 정보
        transportation: 교통수단
        estimated_cost: 예상 비용
    
    Returns:
        생성된 PDF 파일 경로
    """
    try:
        # PDF 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"business_trip_plan_{timestamp}.pdf"
        filepath = os.path.join(os.getcwd(), filename)
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 중앙 정렬
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = styles['Normal']
        
        # 제목
        story.append(Paragraph("Approval Request for Overseas Business Travel", title_style))
        story.append(Spacer(1, 20))
        
        # Summary 섹션
        story.append(Paragraph("Summary", heading_style))
        summary_data = [
            ["Destination", destination],
            ["Travel Period", f"{start_date} ~ {end_date}"],
            ["Purpose", purpose],
            ["Traveler", traveler_name],
            ["Department", department],
            ["Position", position]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Basic Details 섹션
        story.append(Paragraph("Basic Details", heading_style))
        
        basic_details = f"""
        <b>Travel Information:</b><br/>
        • Destination: {destination}<br/>
        • Departure Date: {start_date}<br/>
        • Return Date: {end_date}<br/>
        • Duration: {_calculate_duration(start_date, end_date)} days<br/>
        <br/>
        <b>Accommodation & Transportation:</b><br/>
        • Accommodation: {accommodation}<br/>
        • Transportation: {transportation}<br/>
        • Estimated Cost: {estimated_cost}<br/>
        <br/>
        <b>Business Purpose:</b><br/>
        • {purpose}<br/>
        """
        
        story.append(Paragraph(basic_details, normal_style))
        story.append(Spacer(1, 20))
        
        # Approval Request 섹션
        story.append(Paragraph("Approval Request for Overseas Business Travel", heading_style))
        
        approval_text = f"""
        I hereby request approval for overseas business travel to {destination} 
        from {start_date} to {end_date} for the purpose of {purpose}.
        
        This business trip is essential for our company's operations and will contribute 
        to achieving our business objectives. All necessary preparations have been made 
        to ensure a successful and productive trip.
        
        I will ensure compliance with all company policies and procedures during this 
        business travel and will provide a detailed report upon my return.
        """
        
        story.append(Paragraph(approval_text, normal_style))
        story.append(Spacer(1, 20))
        
        # Key Details 섹션
        story.append(Paragraph("Key Details", heading_style))
        
        key_details_data = [
            ["Item", "Details"],
            ["Travel Destination", destination],
            ["Travel Period", f"{start_date} to {end_date}"],
            ["Business Purpose", purpose],
            ["Accommodation", accommodation],
            ["Transportation", transportation],
            ["Estimated Budget", estimated_cost],
            ["Emergency Contact", "Company HR Department"],
            ["Travel Insurance", "Required"],
            ["Visa Requirements", "To be confirmed"],
            ["Health Precautions", "Standard travel health guidelines"]
        ]
        
        key_table = Table(key_details_data, colWidths=[2*inch, 4*inch])
        key_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(key_table)
        story.append(Spacer(1, 30))
        
        # 서명 섹션
        signature_data = [
            ["Applicant Signature", "Date", "Supervisor Approval", "Date"],
            ["_________________", "___________", "_________________", "___________"],
            [traveler_name, "", "Supervisor Name", ""],
            [position, "", "Supervisor Position", ""]
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(signature_table)
        
        # PDF 생성
        doc.build(story)
        
        return f"✅ 출장 계획서 PDF가 생성되었습니다: {filename}\n📁 파일 위치: {filepath}"
        
    except Exception as e:
        return f"❌ PDF 생성 중 오류가 발생했습니다: {str(e)}"

def _calculate_duration(start_date: str, end_date: str) -> int:
    """출장 기간 계산"""
    try:
        if start_date and end_date:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            return (end - start).days + 1
        return 1
    except:
        return 1

if __name__ == "__main__":
    print("Starting PDF Generator MCP Server...")
    mcp.run(transport="stdio")