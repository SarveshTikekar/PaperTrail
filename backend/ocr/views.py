import cv2
import numpy as np
import pytesseract

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import OCRUploadSerializer


class OCRAPIView(APIView):
    """OCR API: accepts image upload and returns extracted text."""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = OCRUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image_file = serializer.validated_data['image']

        try:
            image_bytes = image_file.read()
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if image is None:
                return Response({'error': 'Invalid image file.'}, status=status.HTTP_400_BAD_REQUEST)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            extracted_text = pytesseract.image_to_string(thresh).strip()

            return Response({'text': extracted_text}, status=status.HTTP_200_OK)

        except pytesseract.TesseractNotFoundError:
            # For development/testing: return mock OCR result when Tesseract is not installed
            return Response({'text': 'Sample OCR Result: This is extracted text from the uploaded image. Please install Tesseract OCR for actual processing.', 'note': 'Tesseract not installed - using mock response'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'OCR processing failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
