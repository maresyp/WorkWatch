from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

admins = {
    'admin': {
        'first_name': 'admin',
        'username': 'admin',
        'password': 'admin',
        'email': 'admin@o2.pl',
    },
}

users = {
    'maresyp': {
        'first_name': 'maresyp',
        'username': 'maresyp',
        'password': 'maresyp',
        'email': 'maresyp@o2.pl',
    },
    'miro': {
        'first_name': 'miro',
        'username': 'miro',
        'password': 'miro',
        'email': 'miro@o2.pl',
    },
}


class Command(BaseCommand):
    help = 'Populates the database with default users, tags and other needed stuff'

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name='Managers')
        if created:
            print("Created 'Managers' group")
        else:
            print("'Managers' group already exists")

        for key, value in admins.items():
            try:
                user = User.objects.create_superuser(**value)
                print(f'Created super-user with parameters: {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} super-user.')

        for key, value in users.items():
            try:
                user = User.objects.create_user(**value)
                group.user_set.add(user)
                print(f'Created managers with parameters: {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} user.')
