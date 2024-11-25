from django.db import models


class LowercaseEmailField(models.EmailField):
    """
    Custom email field that automatically converts email to lowercase
    and enforces uniqueness.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """
        Convert the email to lowercase before saving to database.
        """
        value = super().get_prep_value(value)
        if value is not None:
            value = value.lower()
        return value
