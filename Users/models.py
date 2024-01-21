from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Mężczyzna'),
        ('K', 'Kobieta'),
    ]

    CONTRACT_TYPE_CHOICES = [
        ('1', 'Pełny etat'),
        ('2', 'Pół etatu'),
    ]


    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    city = models.CharField(max_length=50, default="", blank=True)
    street = models.CharField(max_length=255, default="", blank=True)
    house_number = models.CharField(max_length=255, default="", blank=True)
    postal_code = models.CharField(max_length=255, default="", blank=True)
    phone_number = models.CharField(max_length=40, default="", blank=True)
    profile_image = models.ImageField(upload_to='profiles', null=True, blank=True, default='profiles/user-default.png')

    available_leave = models.IntegerField(default=26)
    on_demand_leave = models.IntegerField(default=4)
    parental_leave = models.IntegerField(default=5)
    force_majeure_leave = models.IntegerField(default=2)

    contract_type = models.CharField(max_length=1, choices=CONTRACT_TYPE_CHOICES, default='1')
    

    def __str__(self) -> str:
        return str(self.user)

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except Exception:
            url = ''
        return url


