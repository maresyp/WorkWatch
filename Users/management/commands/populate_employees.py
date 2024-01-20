import random
from abc import ABC, abstractmethod
from collections.abc import Iterable

from django.core.management.base import BaseCommand, CommandParser
from faker import Faker
from faker.providers import BaseProvider

from Users.models import User


class Command(BaseCommand):
    """
    A Django management command class that populates the database with users.

    :param BaseCommand: Inherits from Django's BaseCommand class.
    :type BaseCommand: class
    """
    help = 'Populates the database with the users'

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Adds custom command arguments.

        :param parser: The command line parser.
        :type parser: CommandParser
        """
        parser.add_argument('amount', type=int, help='The number of users to be created')
        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        """
        The function that executes the command logic.

        :param args: Command arguments.
        :type args: tuple
        :param kwargs: Command keyword arguments.
        :type kwargs: dict
        """
        user_generator = UserGenerator()
        existing_emails = set(User.objects.values_list('email', flat=True))
        creations: int = 0

        requested = int(kwargs['amount'])
        if requested < 1:
            raise ValueError("Amount must be greater than 0.")

        print('Keep in mind that creation of Codes involves anti plagiarism checks')
        print('This can take a while. Do not interrupt the process.')

        while creations < requested:
            for data in user_generator.generate(requested - creations):
                if data['email'] in existing_emails:
                    print(f'User with email {data["email"]} already exists. Skipping')
                    continue

                existing_emails.add(data['email'])

                # create user
                user = User.objects.create_user(
                    first_name=data['name'],
                    email=data['email'],
                    username=data['email'].split('@')[0],
                    password='default'
                )

                # create profile for given user
                profile = user.profile
                profile.city = 'Warsaw'
                profile.age = data['age']
                profile.gender = data['gender']
                profile.save()

                creations += 1
                print(f'Created User with email {data["email"]}.')


class Generator(ABC):
    """
    An abstract class for generating mock users.

    :param ABC: Inherits from Python's ABC (Abstract Base Class) class.
    :type ABC: class
    """

    @abstractmethod
    def generate(self, *args, **kwargs):
        """
        Abstract method for generating mock users.

        :param args: Command arguments.
        :type args: tuple
        :param kwargs: Command keyword arguments.
        :type kwargs: dict
        """
        raise NotImplementedError


class UserGenerator(Generator, BaseProvider):
    """
    A class for generating mock users.

    :param Generator: Inherits from the Generator abstract base class.
    :type Generator: class
    :param BaseProvider: Inherits from Faker's BaseProvider class.
    :type BaseProvider: class
    """

    def __init__(self):
        """
        Constructor for UserGenerator class.

        :param available_tags: A list of available tags.
        :type available_tags: list[Tag]
        """
        self.__faker = Faker()
        Faker.seed(2137)
        random.seed(2137)


    def generate(self, amount: int = 1) -> Iterable[dict]:
        """
        Method for generating mock users.

        :param amount: The number of mock users to generate.
        :type amount: int
        :return: A generator yielding user data.
        :rtype: Iterable[dict]
        """
        if amount < 1:
            raise ValueError("Amount must be greater than 0.")

        for _ in range(amount):
            data = dict()
            data["gender"] = random.choice(["M", "F"])
            data["name"] = self.generate_name(data["gender"])
            data["email"] = self.generate_email(data["name"])
            data["pwd"] = self.generate_password()
            data["age"] = random.randint(18, 69)

            yield data

    def generate_name(self, gender: str) -> str:
        """
        Generates a random name based on the provided gender.

        :param gender: The gender of the name ("M" for male, "F" for female).
        :type gender: str
        :return: A random name.
        :rtype: str
        """
        if gender == "M":
            return f'{self.__faker.first_name_male()} {self.__faker.last_name_male()}'.lower()
        return f'{self.__faker.first_name_female()} {self.__faker.last_name_female()}'.lower()

    def generate_email(self, name: str) -> str:
        """
        Generates a random email address from a given name.

        :param name: The name of the user.
        :type name: str
        :return: A random email address.
        :rtype: str
        """
        return f'{name.replace(" ", ".")}{random.randint(0, 2137)}@{self.__faker.free_email_domain()}'.lower()

    def generate_password(self) -> str:
        """
        Generates a random password.

        :return: A random password.
        :rtype: str
        """
        return self.__faker.password(length=25, special_chars=True, digits=True, upper_case=True, lower_case=True)

    def generate_bio(self) -> str:
        """
        Generates a random bio.

        :return: A random bio.
        :rtype: str
        """
        return self.__faker.text(max_nb_chars=150)
