from django.core.management.base import BaseCommand

from Users.models import User

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
    """
    A Django management command class that populates the database with default
    users, and other required items.

    :param BaseCommand: Inherits from Django's BaseCommand class.
    :type BaseCommand: class
    """
    help = 'Populates the database with default users, tags and other needed stuff'

    def handle(self, *args, **kwargs):
        """
        The function that executes the command logic.

        :param args: Command arguments.
        :type args: tuple
        :param kwargs: Command keyword arguments.
        :type kwargs: dict
        """
        # create default admins
        for key, value in admins.items():
            try:
                User.objects.create_superuser(**value)
                print(f'Created super-user with parameters: {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} super-user.')

        # create default users
        for key, value in users.items():
            try:
                User.objects.create_user(**value)
                print(f'Created user with parameters: {value}')
            except Exception as e:
                print(f'Error: {e} during creating {key} user.')
