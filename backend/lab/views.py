import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import PANForm49A, VoterIDForm6
from .serializers import FormUploadSerializer, PANForm49ASerializer, VoterIDForm6Serializer
from .services import preprocess_image, extract_text_from_roi

class FormUploadView(APIView):
    """API for uploading an image and triggering basic OCR processing."""
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = FormUploadSerializer(data=request.data)
        if serializer.is_valid():
            image_file = serializer.validated_data['image']
            form_type = serializer.validated_data['form_type']
            
            # 1. Create the instance
            if form_type == 'pan_49a':
                instance = PANForm49A.objects.create(original_image=image_file)
                # For Sprint 1, we'll return a basic structure to the front-end
                # We can run a full-page text extraction for now
                try:
                    import pytesseract
                    image_path = instance.original_image.path
                    extracted_text = pytesseract.image_to_string(image_path).strip()
                    instance.extracted_data = {'raw_text': extracted_text}
                    instance.save()
                    return Response(PANForm49ASerializer(instance).data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            elif form_type == 'voter_6':
                instance = VoterIDForm6.objects.create(original_image=image_file)
                try:
                    import pytesseract
                    image_path = instance.original_image.path
                    # Use English and Hindi for Voter ID
                    extracted_text = pytesseract.image_to_string(image_path, lang='hin+eng').strip()
                    instance.extracted_data = {'raw_text': extracted_text}
                    instance.save()
                    return Response(VoterIDForm6Serializer(instance).data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({'error': f"Hindi OCR pack may be missing: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
