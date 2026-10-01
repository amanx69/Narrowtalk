import random
from django.core.management.base import BaseCommand
from apps.post.models import Project
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()

class Command(BaseCommand):
    help = 'Seeds the database with 20 dummy projects'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting project seeding...')

        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.WARNING('No users found. Creating a dummy user...'))
            dummy_user = User.objects.create_user(
                email=fake.email(),
                password='password123',
            )
            users.append(dummy_user)

        stages = [choice[0] for choice in Project.Stage.choices]

        created_count = 0
        for _ in range(20):
            owner = random.choice(users)
            
            # Generate a unique project name
            project_name = fake.unique.slug()[:50]
            
            Project.objects.create(
                owner=owner,
                title=fake.catch_phrase()[:150],
                project_name=project_name,
                description=fake.text(max_nb_chars=500),
                stage=random.choice(stages),
                industry=fake.company_suffix()[:100],
                location=fake.city()[:100],
                like_count=random.randint(0, 100),
                view_count=random.randint(50, 500),
                comment_count=random.randint(0, 20),
                save_count=random.randint(0, 50),
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} dummy projects!'))
