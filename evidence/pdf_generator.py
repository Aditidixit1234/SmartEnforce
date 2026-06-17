from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from datetime import datetime
import os

OUTPUT_DIR = "evidence/reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pdf(violation_data: dict) -> str:
    """
    Generate a professional PDF evidence report
    """
    violation_id = violation_data.get('violation_id', 'V000000')
    filename = f"{OUTPUT_DIR}/{violation_id}_report.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    elements = []

    # Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.darkred,
        spaceAfter=10,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.grey,
        alignment=1,
        spaceAfter=20
    )

    # Header
    elements.append(Paragraph("VIOSENSE", title_style))
    elements.append(Paragraph(
        "AI-Powered Traffic Violation Evidence Report",
        subtitle_style
    ))
    elements.append(Spacer(1, 0.2 * inch))

    # Violation ID Banner
    banner_data = [[f"VIOLATION ID: {violation_id}"]]
    banner_table = Table(banner_data, colWidths=[500])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.darkred]),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Risk Level Color
    risk = violation_data.get('risk_level', 'MEDIUM')
    risk_color = {
        'CRITICAL': colors.red,
        'HIGH': colors.orange,
        'MEDIUM': colors.gold,
        'LOW': colors.green
    }.get(risk, colors.orange)

    # Main Details Table
    detail_data = [
        ['FIELD', 'DETAILS'],
        ['Date & Time', violation_data.get('timestamp',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
        ['Vehicle Type', violation_data.get('vehicle_type', 'Unknown')],
        ['License Plate', violation_data.get('plate_number', 'Unknown')],
        ['Violation Type', violation_data.get('violation_type', 'Unknown')],
        ['Severity Score', f"{violation_data.get('severity', 0)}/10"],
        ['Risk Level', risk],
        ['AI Confidence', f"{violation_data.get('confidence', 0)}%"],
        ['Location', violation_data.get('location', 'Unknown')],
        ['Officer Action', violation_data.get('action', 'Pending Review')],
    ]

    detail_table = Table(detail_data, colWidths=[180, 320])
    detail_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Data rows
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
            [colors.lightgrey, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Risk level color
        ('TEXTCOLOR', (1, 6), (1, 6), risk_color),
        ('FONTNAME', (1, 6), (1, 6), 'Helvetica-Bold'),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Repeat Offender Section
    repeat_data = violation_data.get('repeat_offender', {})
    if repeat_data:
        elements.append(Paragraph(
            "REPEAT OFFENDER ANALYSIS",
            ParagraphStyle('Section',
                parent=styles['Heading2'],
                textColor=colors.darkred)
        ))

        offender_data = [
            ['Total Violations', str(repeat_data.get('total_violations', 0))],
            ['Risk Score', f"{repeat_data.get('risk_score', 0)}/10"],
            ['Status', repeat_data.get('status', 'First Offence')],
        ]

        offender_table = Table(offender_data, colWidths=[180, 320])
        offender_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightyellow),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(offender_table)
        elements.append(Spacer(1, 0.3 * inch))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(
        "Generated by VioSense AI Traffic Enforcement Platform",
        footer_style
    ))
    elements.append(Paragraph(
        f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        footer_style
    ))
    elements.append(Paragraph(
        "This is an AI-generated document for law enforcement use only.",
        footer_style
    ))

    # Build PDF
    doc.build(elements)
    print(f"PDF generated: {filename}")
    return filename


if __name__ == "__main__":
    # Test data
    test_violation = {
        'violation_id': 'V20260617001',
        'vehicle_type': 'Motorcycle',
        'plate_number': 'KA01AB1234',
        'violation_type': 'No Helmet',
        'severity': 7.2,
        'risk_level': 'HIGH',
        'confidence': 96.5,
        'location': 'MG Road, Bengaluru',
        'timestamp': '2026-06-17 12:31:00',
        'action': 'Issue Challan',
        'repeat_offender': {
            'total_violations': 3,
            'risk_score': 8.5,
            'status': 'HABITUAL OFFENDER'
        }
    }

    pdf_path = generate_pdf(test_violation)
    print("Evidence PDF generated successfully!")
    print(f"Location: {pdf_path}")