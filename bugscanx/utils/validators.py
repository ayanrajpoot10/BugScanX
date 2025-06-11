import os
import ipaddress
from prompt_toolkit.validation import Validator, ValidationError


def create_validator(validators):
    class CustomValidator(Validator):
        def validate(self, document):
            text = document.text.strip()
            for validator in validators:
                if callable(validator):
                    result = validator(text)
                    if isinstance(result, str):
                        raise ValidationError(
                            message=result,
                            cursor_position=len(text)
                        )
                    elif result is False:
                        raise ValidationError(
                            message="Invalid input",
                            cursor_position=len(text)
                        )
                elif isinstance(validator, dict) and 'fn' in validator:
                    result = validator['fn'](text)
                    if isinstance(result, str) or result is False:
                        message = validator.get('message', "Invalid input")
                        if isinstance(result, str):
                            message = result
                        raise ValidationError(
                            message=message,
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
            return f"Invalid CIDR notation: {cidr}"
    
    return True


def is_digit(text, allow_comma=True):
    if not allow_comma and ',' in text:
        return "Only a single value allowed"
    
    if not text.strip().replace(',', '').replace(' ', '').isdigit():
        return f"Invalid number: {text}"
    return True
