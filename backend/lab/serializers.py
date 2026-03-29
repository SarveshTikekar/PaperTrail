from rest_framework import serializers
from .models import ExtractionMethod, PANForm49A, VoterIDForm6

class PANForm49ASerializer(serializers.ModelSerializer):
    class Meta:
        model = PANForm49A
        fields = '__all__'

class VoterIDForm6Serializer(serializers.ModelSerializer):
    class Meta:
        model = VoterIDForm6
        fields = '__all__'


class ExtractionMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractionMethod
        fields = '__all__'


class FormUploadSerializer(serializers.Serializer):
    """Serializer for handling image upload and form type selection."""
    FORM_TYPES = [
        ('pan_49a', 'PAN Form 49A'),
        ('voter_6', 'Voter ID Form 6'),
    ]
    
    image = serializers.FileField()
    form_type = serializers.ChoiceField(choices=FORM_TYPES)
    extraction_method = serializers.CharField(required=False, allow_blank=True)
