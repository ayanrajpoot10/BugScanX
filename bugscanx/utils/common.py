import os
from InquirerPy import get_style
from InquirerPy.prompts import (
    ListPrompt as select,
    FilePathPrompt as filepath,
    InputPrompt as text,
    ConfirmPrompt as confirm
)
from .validators import create_validator, required, is_file, is_digit, is_cidr

DEFAULT_STYLE = get_style(
    {
        "question": "#87CEEB",
        "answer": "#00FF7F",
        "answered_question": "#808080"
    },
    style_override=False
)

INPUT_VALIDATORS = {
    "file": [required, is_file],
    "number": [required, is_digit],
    "text": [required]
}

INPUT_HANDLERS = {
    "choice": lambda params: select(**params).execute(),
    "file": lambda params: filepath(**params).execute(),
    "number": lambda params: text(**params).execute(),
    "text": lambda params: text(**params).execute()
}

def get_input(
    message,
    input_type="text",
    default=None,
    validators=None,
    choices=None,
    multiselect=False,
    transformer=None,
    style=DEFAULT_STYLE,
    validate_input=True,
    instruction="",
    long_instruction="",
    mandatory=True,
    allow_comma_separated=True,
    **kwargs
):
    common_params = {
        "message": f" {message.strip()}" + ("" if instruction else ":"),
        "default": "" if default is None else str(default),
        "qmark": kwargs.pop("qmark", ""),
        "amark": kwargs.pop("amark", ""),
        "style": style,
        "instruction": instruction + (":" if instruction else ""),
        "mandatory": mandatory,
    }
    
    if validators is None and validate_input:
        validators = INPUT_VALIDATORS.get(input_type, [])
        
    if validate_input and validators:
        if input_type == "number":
            validators = [lambda x: is_digit(x, allow_comma_separated)]
        common_params["validate"] = create_validator(validators)
    
    input_type_params = {
        "choice": {
            "choices": choices,
            "multiselect": multiselect,
            "transformer": transformer,
            "show_cursor": kwargs.pop("show_cursor", False),
            "long_instruction": long_instruction or "Use ↑ ↓ to navigate, Enter to select."
        },
        "file": {
            "only_files": kwargs.pop("only_files", True)
        }
    }
    
    common_params.update(input_type_params.get(input_type, {}))
    common_params.update(kwargs)
    
    handler = INPUT_HANDLERS.get(input_type)
    if not handler:
        raise ValueError(f"Unsupported input_type: {input_type}")
    
    return handler(common_params)

def get_confirm(
    message,
    default=True,
    style=DEFAULT_STYLE,
    **kwargs
):
    return confirm(
        message=message,
        default=default,
        qmark="",
        amark="",
        style=style,
        **kwargs
    ).execute()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
