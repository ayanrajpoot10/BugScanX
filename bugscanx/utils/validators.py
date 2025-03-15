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
                        raise ValidationError(message=result, cursor_position=len(text))
                    elif result is False:
                        raise ValidationError(message="Invalid input", cursor_position=len(text))
                elif isinstance(validator, dict) and 'fn' in validator:
                    result = validator['fn'](text)
                    if isinstance(result, str) or result is False:
                        message = validator.get('message', "Invalid input")
                        if isinstance(result, str):
                            message = result
                        raise ValidationError(message=message, cursor_position=len(text))
    
    return CustomValidator()

def required(text):
    return bool(text.strip()) or "Input cannot be empty"

def is_file(text):
    return os.path.isfile(text) or f"File does not exist: {text}"

def is_cidr(text):
    if not text.strip():
        return "CIDR input cannot be empty"
    
    parts = [p.strip() for p in text.split(',') if p.strip()]
    for part in parts:
        try:
            ipaddress.ip_network(part, strict=False)
        except ValueError:
            return f"Invalid CIDR notation: {part}"
    return True

def is_digit(text):
    if not text.strip():
        return True
    
    parts = text.split(',')
    for part in parts:
        part = part.strip()
        if part and not part.isdigit():
            return f"Not a valid number: {part}"
    return True
