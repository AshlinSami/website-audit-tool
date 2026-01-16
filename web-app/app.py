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
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
                    auditor = WebsiteAuditor(
                        url, 
                        max_pages=max_pages, 
                        progress_queue=q,
                        ai_enabled=True,
                        openai_api_key=os.environ.get('OPENAI_API_KEY')
                    )
                    report = auditor.run_audit()
                    
                    # Save report to file
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f'audit-report-{timestamp}.json'
                    auditor.save_report(report, filename)
                    print(f"✅ Report saved: {filename}")
                    
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
    
    # Professional Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#0ea5e9'),
        spaceAfter=14,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderColor=colors.HexColor('#0ea5e9'),
        borderPadding=8
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )
    
    # Professional Header
    story.append(Paragraph("Website Audit Report", title_style))
    story.append(Paragraph("Comprehensive Performance Analysis", subtitle_style))
    
    # Info box
    info_data = [[f"<b>Website:</b> {report['url']}", 
                  f"<b>Date:</b> {datetime.fromisoformat(report['timestamp']).strftime('%B %d, %Y')}"]]
    info_table = Table(info_data, colWidths=[3.5*inch, 2.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1'))
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.4 * inch))
    
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Recommendations Section with AI Enhancement
    story.append(Paragraph("Recommendations & Implementation Plan", heading_style))
    
    # Sort by AI priority score if available
    sorted_recs = sorted(report['recommendations'], 
                         key=lambda x: x.get('ai_priority_score', 5), 
                         reverse=True)
    
    for i, rec in enumerate(sorted_recs, 1):
        priority = "🔴 CRITICAL" if rec['priority'] == 'critical' else "🟡 WARNING"
        ai_score = rec.get('ai_priority_score', 'N/A')
        
        story.append(Paragraph(f"<b>{i}. [{rec['category']}] {rec['title']}</b>", styles['Normal']))
        story.append(Paragraph(f"<i>Priority: {priority} | Impact Score: {ai_score}/10</i>", styles['Normal']))
        
        # Use AI recommendation if available, otherwise use default
        if rec.get('ai_recommendation'):
            ai_rec = rec['ai_recommendation'].replace('\n', '<br/>')
            story.append(Paragraph(ai_rec, styles['Normal']))
        else:
            story.append(Paragraph(f"Description: {rec['description']}", styles['Normal']))
            story.append(Paragraph(f"<b>Recommendation:</b> {rec['recommendation']}", styles['Normal']))
        
        story.append(Spacer(1, 0.2 * inch))
    
    # Detailed Issues Section
    if report.get('detailed_issues'):
        story.append(PageBreak())
        story.append(Paragraph("Detailed Issues & Fixes", heading_style))
        
        from collections import defaultdict
        grouped = defaultdict(list)
        for issue in report['detailed_issues']:
            grouped[issue.get('category', 'Other')].append(issue)
        
        for category, issues in grouped.items():
            cat_style = ParagraphStyle('Category', parent=styles['Heading3'], 
                                      fontSize=12, textColor=colors.HexColor('#64748b'), spaceAfter=8)
            story.append(Paragraph(f"{category} ({len(issues)} issues)", cat_style))
            
            for i, issue in enumerate(issues, 1):  # Show ALL issues
                story.append(Paragraph(f"<b>{i}. {issue.get('title', 'Unknown')}</b>", styles['Normal']))
                story.append(Paragraph(f"Page: {issue.get('page', 'N/A')}", styles['Normal']))
                
                if issue.get('current'):
                    current_text = str(issue.get('current'))[:150]  # Limit length
                    story.append(Paragraph(f"<font color='#dc2626'>Current: {current_text}</font>", styles['Normal']))
                
                if issue.get('fix'):
                    story.append(Paragraph(f"<font color='#059669'>Fix: {issue.get('fix')}</font>", styles['Normal']))
                
                story.append(Spacer(1, 0.1 * inch))
            
            
            story.append(Spacer(1, 0.15 * inch))
    
    # Page Performance Section
    if report.get('page_speeds'):
        story.append(PageBreak())
        story.append(Paragraph("Page Performance Metrics", heading_style))
        
        perf_data = [['Page', 'Load Time', 'LCP', 'CLS', 'FID']]
        
        for page in report['page_speeds']:  # First 20 pages
            page_name = page['page'][:45] if len(page['page']) > 45 else page['page']
            perf_data.append([
                page_name,
                f"{page['loadTime']}s",
                f"{page['lcp']}s",
                f"{page['cls']:.3f}",
                f"{page['fid']}ms"
            ])
        
        perf_table = Table(perf_data, colWidths=[2.5*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(perf_table)
        
        if False:  # Show all pages
            story.append(Spacer(1, 0.1 * inch))
            story.append(Paragraph(f"<i>...and {len(report['page_speeds'])-20} more pages</i>", styles['Italic']))
    
    # Page Break before broken links
    if report.get('broken_links'):
        story.append(PageBreak())
        story.append(Paragraph("Broken Links", heading_style))
        
        for link in report['broken_links']:
            story.append(Paragraph(f"• {link['url']} (Status: {link['status']})", styles['Normal']))
        
        if False:  # Show all links
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