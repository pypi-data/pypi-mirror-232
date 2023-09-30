from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# validation function help us to difine type file and memory of limit of file
def validate_file_extension(value):
    allowed_extensions = ['pdf', 'doc', 'docx']

    validator = FileExtensionValidator(allowed_extensions=allowed_extensions)
    
    try:
        validator(value)
    except ValidationError:
        raise ValidationError('Invalid file extension.')


