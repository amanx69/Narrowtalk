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


class CompressedMediaFileField(serializers.FileField):
    """
    Intelligently compresses and formats Cloudinary media files:
    - Videos: Uses q_auto,w_720 under /video/upload/ for compressed streaming.
    - Images: Uses q_auto,f_auto,w_1080 for responsive, optimized formats.
    - Documents/PDFs & Raw files: Preserves original URL without broken transformations.
    """
    def to_representation(self, value):
        url = super().to_representation(value)
        if not url:
            return url
        lower = url.lower()

        # Raw files and PDFs must never have transformations (returns 400 Bad Request)
        if '/raw/upload/' in lower or lower.endswith('.pdf'):
            return url

        # Videos under video/upload
        video_exts = ('.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.m4v', '.3gp', '.wmv', '.ts')
        if '/video/upload/' in lower or lower.endswith(video_exts):
            if '/video/upload/' in url:
                return url.replace('/video/upload/', '/video/upload/q_auto,w_720/')
            return url

        # Images
        img_exts = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp')
        if '/image/upload/' in lower or lower.endswith(img_exts):
            if '/image/upload/' in url:
                return url.replace('/image/upload/', '/image/upload/q_auto,f_auto,w_1080/')
            elif '/upload/' in url:
                return url.replace('/upload/', '/upload/q_auto,f_auto,w_1080/')

        return url


def get_cloudinary_thumbnail(url, width=300, height=300):
    """
    Generates a fast, optimized Cloudinary thumbnail URL for images and videos:
    - Videos: Extracts the best frame (so_auto) and converts to .jpg format.
    - Images: Delivers a compact (w_300, h_300, c_fill) WebP/auto formatted image.
    - Documents/PDFs: Returns None (or original URL) to preserve raw file integrity.
    """
    if not url:
        return None
    lower = url.lower()

    # Raw files & PDFs do not support direct thumbnail transformation
    if '/raw/upload/' in lower or lower.endswith('.pdf'):
        return None

    import re

    # Videos: replace extension with .jpg and add so_auto thumbnail transformation
    video_exts = ('.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.m4v', '.3gp', '.wmv', '.ts')
    if '/video/upload/' in lower or any(lower.endswith(ext) for ext in video_exts):
        jpg_url = re.sub(
            r'\.(mp4|mov|avi|webm|mkv|flv|m4v|3gp|wmv|ts)(\?.*)?$',
            '.jpg',
            url,
            flags=re.IGNORECASE,
        )
        if '/video/upload/' in jpg_url:
            return re.sub(
                r'/video/upload/(?:[a-zA-Z0-9_,]+)?/?',
                f'/video/upload/so_auto,w_{width},h_{height},c_fill,q_auto,f_auto/',
                jpg_url,
            )
        return jpg_url

    # Images: add compact crop
    if '/upload/' in url:
        return re.sub(
            r'/upload/(?:[a-zA-Z0-9_,]+)?/?',
            f'/upload/w_{width},h_{height},c_fill,q_auto,f_auto/',
            url,
        )

    return url




