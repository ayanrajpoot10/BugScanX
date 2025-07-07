import os
import ipaddress
from prompt_toolkit.validation import Validator, ValidationError


def create_validator(*validators):
    class CustomValidator(Validator):
        def validate(self, document):
            text = document.text.strip()
            for validator in validators:
                if callable(validator):
                    result = validator(text)
                    if result is not True:
                        error_message = result if isinstance(result, str) else "Invalid input"
                        raise ValidationError(
                            message=error_message,
                            cursor_position=len(text)
                        )
    return CustomValidator()


def required(text):
    return True if text.strip() else "Input is required."


def is_file(text):
    return os.path.isfile(text) or f"File not found: {text}"


def is_cidr(text):
    if not text.strip():
        return "CIDR input cannot be empty"
    
    cidrs = [cidr.strip() for cidr in text.split(',')]
    
    for cidr in cidrs:
        if not cidr:
            continue
        try:
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            return f"Invalid CIDR: {cidr}"
    
    return True


def is_digit(text, allow_comma=True):
    if not allow_comma and ',' in text:
        return "Only a single value allowed"
    
    clean_text = text.strip().replace(',', '').replace(' ', '')
    if not clean_text or not clean_text.isdigit():
        return f"Invalid number: {text}"
    return True


VALIDATORS = {
    'required': [required],
    'file': [required, is_file],
    'number': [required, is_digit],
    'cidr': [required, is_cidr],
}
