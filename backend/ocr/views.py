import cv2
import numpy as np
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import OCRUploadSerializer


class OCRAPIView(APIView):
    """OCR API: accepts image or PDF upload and returns extracted text."""

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = OCRUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = serializer.validated_data['image']
        file_name = uploaded_file.name.lower()

        try:
            # Import pytesseract only when needed to avoid startup issues
            import pytesseract
            if settings.TESSERACT_CMD:
                pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

            # Tesseract path for Windows (default installation location)
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            extracted_text = ""

            # Check if file is PDF
            if file_name.endswith('.pdf'):
                # Process PDF file
                try:
                    from pdf2image import convert_from_bytes

                    # Convert PDF to images
                    images = convert_from_bytes(uploaded_file.read())

                    for i, image in enumerate(images):
                        # Convert PIL image to OpenCV format
                        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                        # Preprocess image
                        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
                        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

                        # Extract text from this page
                        page_text = pytesseract.image_to_string(thresh).strip()
                        if page_text:
                            extracted_text += f"\n--- Page {i+1} ---\n{page_text}\n"

                except ImportError:
                    return Response({'error': 'PDF processing not available. Please install pdf2image.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    return Response({'error': f'PDF processing failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                # Process image file (existing logic)
                image_bytes = uploaded_file.read()
                np_arr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if image is None:
                    return Response({'error': 'Invalid image file.'}, status=status.HTTP_400_BAD_REQUEST)

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

                extracted_text = pytesseract.image_to_string(thresh).strip()

            return Response({'text': extracted_text.strip()}, status=status.HTTP_200_OK)

        except ImportError:
            return Response(
                {'error': 'pytesseract is not installed in the backend environment.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return Response(
                {'error': f'OCR processing failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
