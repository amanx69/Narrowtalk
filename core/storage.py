import os
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.core.files.uploadedfile import UploadedFile

class AutoMediaCloudinaryStorage(RawMediaCloudinaryStorage):
    def _get_resource_type(self, name):
        ext = os.path.splitext(name)[1].lower()
        video_extensions = [
            '.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv',
            '.m4v', '.3gp', '.wmv', '.ts'
        ]
        if ext in video_extensions or 'VID_' in name:
            return 'video'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.svg']:
            return 'image'
        return 'raw'

    def _save(self, name, content):
        name = self._normalise_name(name)
        name = self._prepend_prefix(name)
        ext = os.path.splitext(name)[1].lower()
        content = UploadedFile(content, name)
        response = self._upload(name, content)
        public_id = response['public_id']

        # Ensure extension is preserved so Django and Cloudinary know the media format
        format_ext = response.get('format')
        if format_ext:
            format_ext = f".{format_ext.lower()}"
        else:
            format_ext = ext

        if format_ext and not public_id.lower().endswith(format_ext):
            return f"{public_id}{format_ext}"
        return public_id

    def delete(self, name):
        import cloudinary.uploader
        name = self._normalise_name(name)
        resource_type = self._get_resource_type(name)

        # In Cloudinary:
        # - 'raw' files keep extension in public_id
        # - 'image' and 'video' files typically do NOT have extensions in public_id
        without_ext = os.path.splitext(name)[0]
        public_ids_to_try = [without_ext, name] if resource_type in ['image', 'video'] else [name, without_ext]

        for pid in public_ids_to_try:
            try:
                res = cloudinary.uploader.destroy(pid, invalidate=True, resource_type=resource_type)
                if res.get('result') == 'ok':
                    return True
            except Exception:
                pass

        # Fallback check across all resource types if initial attempt was 'not found'
        for fallback_type in ['image', 'video', 'raw']:
            if fallback_type == resource_type:
                continue
            for pid in public_ids_to_try:
                try:
                    res = cloudinary.uploader.destroy(pid, invalidate=True, resource_type=fallback_type)
                    if res.get('result') == 'ok':
                        return True
                except Exception:
                    pass

        return False

