from rest_framework import serializers

class CompressedProfilePicField(serializers.ImageField):
    """
    used for profile picture compression for User Profile Page (500x500).
    Adds Cloudinary transformations for auto-format and auto-quality.
    """
    def to_representation(self, value):
        url = super().to_representation(value)
        if url and '/upload/' in url:
            return url.replace('/upload/', '/upload/q_auto,f_auto,c_fill,w_500,h_500/')
        return url

class ThumbnailProfilePicField(serializers.ImageField):
    """
    used for Feeds, Chats, and Comments (100x100).
    for small profile images 
    """
    
    def to_representation(self, value):
        url = super().to_representation(value)
        if url and '/upload/' in url:
            return url.replace('/upload/', '/upload/q_auto,f_auto,c_fill,w_100,h_100/')
        return url


