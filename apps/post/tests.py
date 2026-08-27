from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.Profile.api.serializer import SkillSerializer
from apps.Profile.models import Skill
from apps.post.api.serializers import CreateJobRoleSerializer
from apps.post.models import Project


 