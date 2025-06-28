# app1/views.py
import json
import uuid
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from services.ai_services import AIWorksheetService
from .models import Worksheet
from services.pdf_services import PDFGenerator

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class GenerateWorksheetView(View):
    """Generate personalized worksheet based on mood and subject"""
    
    def post(self, request):
        try:
            # Parse request data
            data = json.loads(request.body)
            mood = data.get('mood', '').strip()
            subject = data.get('subject', '').strip()
            grade = data.get('grade', '5-10')
            
            # Validate input
            if not mood:
                return JsonResponse({
                    'error': 'Mood is required',
                    'message': 'Please tell us how you\'re feeling today!'
                }, status=400)
            
            if not subject:
                return JsonResponse({
                    'error': 'Subject is required',
                    'message': 'Please choose a subject to get started!'
                }, status=400)
            
            # Validate subject
            valid_subjects = ['math', 'science']
            if subject not in valid_subjects:
                return JsonResponse({
                    'error': 'Invalid subject',
                    'message': f'Subject must be one of: {", ".join(valid_subjects)}'
                }, status=400)
            
            # Generate worksheet using AI service
            ai_service = AIWorksheetService()
            worksheet_data = ai_service.create_personalized_worksheet(
                mood_input=mood,
                subject=subject,
                grade_level=grade
            )
            
            # Create unique worksheet ID
            worksheet_id = str(uuid.uuid4())
            
            # Save worksheet to database (optional)
            try:
                worksheet = Worksheet.objects.create(
                    worksheet_id=worksheet_id,
                    mood_input=mood,
                    subject=subject,
                    grade_level=grade,
                    motivation=worksheet_data.get('motivation'),
                    questions=worksheet_data.get('questions'),
                    mood_analysis=worksheet_data.get('mood_analysis')
                )
            except Exception as db_error:
                logger.warning(f"Failed to save worksheet to database: {db_error}")
                # Continue without database save
            
            # Prepare response
            response_data = {
                'worksheet_id': worksheet_id,
                'motivation': worksheet_data.get('motivation'),
                'motivationEmoji': worksheet_data.get('motivationEmoji'),
                'questions': worksheet_data.get('questions'),
                'mood_analysis': worksheet_data.get('mood_analysis'),
                'subject': subject,
                'grade_level': grade,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Worksheet generated successfully: {worksheet_id}")
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON',
                'message': 'Please check your request format'
            }, status=400)
        
        except Exception as e:
            logger.error(f"Error generating worksheet: {str(e)}")
            return JsonResponse({
                'error': 'Generation failed',
                'message': 'Something went wrong while creating your worksheet. Please try again!'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GeneratePDFView(View):
    """Generate PDF from worksheet data"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Extract required data
            worksheet_id = data.get('worksheet_id')
            mood = data.get('mood')
            subject = data.get('subject')
            motivation = data.get('motivation')
            motivation_emoji = data.get('motivationEmoji')
            questions = data.get('questions')
            
            if not all([worksheet_id, mood, subject, motivation, questions]):
                return JsonResponse({
                    'error': 'Missing required data',
                    'message': 'Incomplete worksheet data for PDF generation'
                }, status=400)
            
            # Generate PDF
            pdf_generator = PDFGenerator()
            pdf_buffer = pdf_generator.generate_worksheet_pdf({
                'worksheet_id': worksheet_id,
                'mood': mood,
                'subject': subject,
                'motivation': motivation,
                'motivationEmoji': motivation_emoji,
                'questions': questions,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Create response
            response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
            filename = f"ZappyLearn_{subject}_{worksheet_id[:8]}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(pdf_buffer.getvalue())
            
            logger.info(f"PDF generated successfully for worksheet: {worksheet_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            return JsonResponse({
                'error': 'PDF generation failed',
                'message': 'Failed to generate PDF. Please try again!'
            }, status=500)

class WorksheetDetailView(View):
    """Get worksheet details by ID"""
    
    def get(self, request, worksheet_id):
        try:
            worksheet = Worksheet.objects.get(worksheet_id=worksheet_id)
            
            return JsonResponse({
                'worksheet_id': str(worksheet.worksheet_id),
                'mood_input': worksheet.mood_input,
                'subject': worksheet.subject,
                'grade_level': worksheet.grade_level,
                'motivation': worksheet.motivation,
                'questions': worksheet.questions,
                'mood_analysis': worksheet.mood_analysis,
                'created_at': worksheet.created_at.isoformat()
            })
            
        except Worksheet.DoesNotExist:
            return JsonResponse({
                'error': 'Worksheet not found',
                'message': 'The requested worksheet could not be found'
            }, status=404)
        
        except Exception as e:
            logger.error(f"Error retrieving worksheet: {str(e)}")
            return JsonResponse({
                'error': 'Retrieval failed',
                'message': 'Failed to retrieve worksheet'
            }, status=500)

class HealthCheckView(View):
    """Health check endpoint"""
    
    def get(self, request):
        try:
            # Basic health check
            return JsonResponse({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'ZappyLearn Backend'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, status=500)