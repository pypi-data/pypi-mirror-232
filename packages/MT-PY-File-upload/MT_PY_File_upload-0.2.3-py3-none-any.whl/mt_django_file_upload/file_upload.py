from django.core.exceptions import ValidationError
from django.db.models import FileField,ImageField
from django.core.validators import FileExtensionValidator

from django.db.models import FileField

from django.forms import FileField as f_FileField

# Using default django FileField
class Mt_fileUploadField(FileField):
    pass


class Mt_form_fileUploadField(f_FileField):
    pass

class Mt_FileField(FileField):
    def __init__(self, *args, allowed_extensions=None, **kwargs):
        self.allowed_extensions = allowed_extensions or []
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)

        # Use Django's FileExtensionValidator to validate the file extension
        validator = FileExtensionValidator(allowed_extensions=self.allowed_extensions)

        # Validate the file
        try:
            validator(value)
        except ValidationError as e:
            # If the file is not valid, raise a ValidationError with a custom error message
            raise ValidationError('Invalid file format. Only {} files are allowed.'.format(
                ', '.join(self.allowed_extensions))
            ) from e

    # def deconstruct(self):
    #     name, path, args, kwargs = super().deconstruct()
    #     kwargs['txt','doc'] = self.allowed_extensions
    #     return name, path, args, kwargs