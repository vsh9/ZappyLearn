# app1/utils/pdf_generator.py
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PDFGenerator:
    """Generate PDF worksheets"""
    
    def __init__(self):
        self.pagesize = letter
        self.margin = 0.75 * inch
        
    def generate_worksheet_pdf(self, worksheet_data):
        """Generate a PDF worksheet from data"""
        
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=self.margin,
            leftMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        # Build content
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#4A90E2'),
            alignment=TA_CENTER,
            spaceAfter=30,
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#333333'),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        
        motivation_style = ParagraphStyle(
            'MotivationStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=HexColor('#2E7D32'),
            alignment=TA_CENTER,
            spaceAfter=25,
            borderWidth=1,
            borderColor=HexColor('#E8F5E8'),
            borderPadding=15,
            backColor=HexColor('#F8FFF8')
        )
        
        question_header_style = ParagraphStyle(
            'QuestionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#FF6B35'),
            spaceAfter=10,
        )
        
        question_style = ParagraphStyle(
            'QuestionStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            leftIndent=20,
        )
        
        # Add content
        # Title
        story.append(Paragraph("ZappyLearn", title_style))
        story.append(Paragraph("Personalized Learning Worksheet", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Worksheet info
        subject_title = worksheet_data.get('subject', '').title()
        mood_emoji = worksheet_data.get('motivationEmoji', '🌟')
        
        story.append(Paragraph(f"Subject: {subject_title} {mood_emoji}", subtitle_style))
        story.append(Paragraph(f"Generated on: {worksheet_data.get('timestamp', '')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Motivation section
        motivation_text = f"{mood_emoji} {worksheet_data.get('motivation', '')}"
        story.append(Paragraph("Your Personal Motivation", question_header_style))
        story.append(Paragraph(motivation_text, motivation_style))
        story.append(Spacer(1, 20))
        
        # Questions section
        story.append(Paragraph("Practice Questions", question_header_style))
        story.append(Spacer(1, 10))
        
        questions = worksheet_data.get('questions', {})
        difficulty_icons = {
            'easy': '🟢 EASY',
            'medium': '🟡 MEDIUM',
            'hard': '🔴 HARD'
        }
        
        for difficulty in ['easy', 'medium', 'hard']:
            if difficulty in questions and questions[difficulty]:
                # Difficulty header
                difficulty_text = difficulty_icons.get(difficulty, difficulty.upper())
                story.append(Paragraph(f"<b>{difficulty_text}</b>", question_header_style))
                
                # Question text
                question_text = questions[difficulty]
                story.append(Paragraph(question_text, question_style))
                
                # Add space for answer
                story.append(Paragraph("Answer:", styles['Normal']))
                story.append(Spacer(1, 40))  # Space for student to write
                
                story.append(Spacer(1, 20))
        
        # Footer
        story.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=TA_CENTER,
        )
        story.append(Paragraph("Keep learning and growing! 🌟", footer_style))
        story.append(Paragraph(f"Worksheet ID: {worksheet_data.get('worksheet_id', '')}", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer