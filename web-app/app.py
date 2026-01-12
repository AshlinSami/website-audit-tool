#!/usr/bin/env python3
"""
Flask Web Application for Website Audit Tool
"""

from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
from flask_cors import CORS
import sys
import os
from datetime import datetime
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
import queue
import threading
import uuid

# Add the backend directory to the path
sys.path.append(os.path.dirname(__file__))
from website_auditor import WebsiteAuditor

app = Flask(__name__)
CORS(app)

# Global dictionary to store progress queues
progress_queues = {}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/audit-stream', methods=['POST'])
def run_audit_stream():
    """Run website audit with streaming progress updates"""
    try:
        data = request.json
        url = data.get('url')
        max_pages = data.get('max_pages', 50)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Create a unique ID for this audit
        audit_id = str(uuid.uuid4())
        progress_queues[audit_id] = queue.Queue()
        
        def generate():
            """Generator function for Server-Sent Events"""
            q = progress_queues[audit_id]
            
            # Run audit in background thread
            def run_in_background():
                try:
                    auditor = WebsiteAuditor(url, max_pages=max_pages, progress_queue=q)
                    report = auditor.run_audit()
                    q.put({'type': 'complete', 'data': report})
                except Exception as e:
                    q.put({'type': 'error', 'message': str(e)})
            
            thread = threading.Thread(target=run_in_background)
            thread.daemon = True
            thread.start()
            
            # Stream progress updates
            while True:
                try:
                    msg = q.get(timeout=60)
                    yield f"data: {json.dumps(msg)}\n\n"
                    
                    if msg.get('type') in ['complete', 'error']:
                        break
                except queue.Empty:
                    # Send heartbeat to keep connection alive
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
            
            # Cleanup
            if audit_id in progress_queues:
                del progress_queues[audit_id]
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF report"""
    try:
        data = request.json
        report = data.get('report')
        
        if not report:
            return jsonify({'error': 'Report data is required'}), 400
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(report)
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"audit-report-{timestamp}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_pdf_report(report):
    """Generate PDF report from audit results"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0891b2'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0891b2'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("Website Audit Report", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Basic Info
    story.append(Paragraph(f"<b>URL:</b> {report['url']}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.fromisoformat(report['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    # Scores Section
    story.append(Paragraph("Overall Scores", heading_style))
    
    scores_data = [
        ['Category', 'Score'],
        ['Overall', f"{report['scores']['overall']}/100"],
        ['Performance', f"{report['scores']['performance']}/100"],
        ['SEO', f"{report['scores']['seo']}/100"],
        ['Accessibility', f"{report['scores']['accessibility']}/100"],
        ['Best Practices', f"{report['scores']['bestPractices']}/100"],
    ]
    
    scores_table = Table(scores_data, colWidths=[3*inch, 2*inch])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(scores_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Statistics Section
    story.append(Paragraph("Statistics", heading_style))
    
    stats_data = [
        ['Metric', 'Count'],
        ['Pages Crawled', str(report['statistics']['total_pages'])],
        ['Broken Links', str(report['statistics']['broken_links'])],
        ['Redirects', str(report['statistics']['redirects'])],
        ['External Links', str(report['statistics']['external_links'])],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Recommendations Section
    story.append(Paragraph("Recommendations", heading_style))
    
    for i, rec in enumerate(report['recommendations'], 1):
        priority = "🔴 CRITICAL" if rec['priority'] == 'critical' else "🟡 WARNING"
        story.append(Paragraph(f"<b>{i}. [{rec['category']}] {rec['title']}</b>", styles['Normal']))
        story.append(Paragraph(f"<i>Priority: {priority}</i>", styles['Normal']))
        story.append(Paragraph(f"Description: {rec['description']}", styles['Normal']))
        story.append(Paragraph(f"<b>Recommendation:</b> {rec['recommendation']}", styles['Normal']))
        story.append(Spacer(1, 0.15 * inch))
    
    # Page Break before broken links
    if report.get('broken_links'):
        story.append(PageBreak())
        story.append(Paragraph("Broken Links", heading_style))
        
        for link in report['broken_links'][:20]:
            story.append(Paragraph(f"• {link['url']} (Status: {link['status']})", styles['Normal']))
        
        if len(report['broken_links']) > 20:
            story.append(Paragraph(f"...and {len(report['broken_links']) - 20} more", styles['Italic']))
    
    # Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Generated by Algorithm Agency Website Audit Tool", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)