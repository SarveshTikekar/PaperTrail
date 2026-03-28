from rest_framework import serializers

class OCRUploadSerializer(serializers.Serializer):
    image = serializers.FileField(required=True, allow_empty_file=False)
