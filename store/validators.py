from django.core.validators import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_min_value(value):
    if value < 0:
        raise ValidationError(
            _("%(value)s must be positive"),
            params={"value": value},
        )
