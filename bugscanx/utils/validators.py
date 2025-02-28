import os
import ipaddress
from typing import Callable, List, Dict, Any, Union, Optional
from prompt_toolkit.validation import Validator, ValidationError

ValidatorFn = Callable[[str], Union[bool, str]]

class ValidationResult:
    def __init__(self, valid: bool, message: Optional[str] = None):
        self.valid = valid
        self.message = message

def create_validator(validators: List[Union[ValidatorFn, Dict[str, Any]]]) -> Validator:
    
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

# ---------- Common Validators ----------

def required(text: str) -> Union[bool, str]:
    return bool(text.strip()) or "Input cannot be empty"

def is_file(text: str) -> Union[bool, str]:
    return os.path.isfile(text) or f"File does not exist: {text}"

def is_directory(text: str) -> Union[bool, str]:
    return os.path.isdir(text) or f"Directory does not exist: {text}"

def is_cidr(text: str) -> Union[bool, str]:
    if not text.strip():
        return "CIDR input cannot be empty"
        
    parts = [p.strip() for p in text.split(',') if p.strip()]
    for part in parts:
        try:
            ipaddress.ip_network(part, strict=False)
        except ValueError:
            return f"Invalid CIDR notation: {part}"
    return True

def is_digit(text: str) -> Union[bool, str]:
    if not text.strip():
        return True
    
    parts = [p.strip() for p in text.split(',')]
    for part in parts:
        if not part.isdigit():
            return f"Not a valid number: {part}"
    return True

def regex_match(pattern: str, message: str = None) -> ValidatorFn:
    import re
    compiled = re.compile(pattern)
    
    def validator(text: str) -> Union[bool, str]:
        if compiled.match(text):
            return True
        return message or f"Input must match pattern: {pattern}"
    return validator
