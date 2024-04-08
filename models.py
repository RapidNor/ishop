from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings

class User_account (models.Model) :
    name = models.Charfield(
        max_length=50,
        validators=[MinLengthValidator(2, "Name Must Not Be Shorter Than 2 Characters")]

    )
    text = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        return(self.name)