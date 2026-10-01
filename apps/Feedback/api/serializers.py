from ..models import AppFeedback
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


BAD_WORDS_LIST = ['fuck', 'asshole', 'motherfucker', 'pussy', 'land'] 
class CompressedFileField(serializers.FileField):
    def to_representation(self, value):
        url = super().to_representation(value)
        if url and '/upload/' in url:
            if url.endswith('.pdf'):
                return url
            if url.endswith(('.mp4', '.mov', '.avi', '.webm')):
                return url.replace('/upload/', '/upload/q_auto,f_auto,w_720/')
                
            
            return url.replace('/upload/', '/upload/q_auto,f_auto,w_1080/')
        return url
class FeedBackSerializer(serializers.ModelSerializer):
    attachment=CompressedFileField(required=False)
    class Meta:
        model=AppFeedback
        fields=('feedback_type','title','description','attachment')
        
        
    def validate_text_for_bad_words(self, text):
        if not text:
            return text
            
        text_lower = text.lower()
        for word in BAD_WORDS_LIST:
            if word in text_lower:
                raise ValidationError(f"Inappropriate language detected. Please maintain a professional tone.")
        return text
    def validate_title(self, value):
        return self.validate_text_for_bad_words(value)
    def validate_description(self, value):
        return self.validate_text_for_bad_words(value)
    def validate_attachment(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 5MB.")
        return value