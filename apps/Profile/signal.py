import re
import uuid
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile

User = get_user_model()


def _generate_unique_username(email: str | None) -> str:
    """Generate a unique valid username between 4 and 25 characters."""
    base = email.split('@')[0] if email else "user"
    base = re.sub(r'[^a-zA-Z0-9_]', '', base).lower()
    if len(base) < 4:
        base = (base + "user")[:4]
    base = base[:18]

    candidate = base
    while Profile.objects.filter(username__iexact=candidate).exists():
        candidate = f"{base[:18]}_{uuid.uuid4().hex[:5]}"

    return candidate


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        username = _generate_unique_username(getattr(instance, 'email', None))
        Profile.objects.create(user=instance, username=username)