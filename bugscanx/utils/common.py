import os
from InquirerPy import get_style
from InquirerPy.prompts import (
    ListPrompt as select,
    FilePathPrompt as filepath,
    InputPrompt as text,
    ConfirmPrompt as confirm
)
from .validators import create_validator, required, is_file, is_digit

DEFAULT_STYLE = get_style(
    {
        "question": "#87CEEB",
        "answer": "#00FF7F",
        "answered_question": "#808080"
    },
    style_override=False
)

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
    **kwargs
):
    message = f" {message}:"
    common_params = {
        "message": message,
        "default": "" if default is None else str(default),
        "qmark": kwargs.pop("qmark", ""),
        "amark": kwargs.pop("amark", ""),
        "style": style,
        "instruction": instruction,
    }
    
    if validators is None and validate_input:
        validators = {
            "file": [required, is_file],
            "number": [required, is_digit],
            "text": [required]
        }.get(input_type)
    
    validator = create_validator(validators) if validators and validate_input else None
    
    if input_type == "choice":
        return select(
            choices=choices,
            multiselect=multiselect,
            transformer=transformer,
            show_cursor=kwargs.pop("show_cursor", False),
            **common_params,
            **kwargs
        ).execute()
    
    if input_type == "file":
        return filepath(
            validate=validator,
            only_files=kwargs.pop("only_files", True),
            **common_params,
            **kwargs
        ).execute()
    
    if input_type in ["number", "text"]:
        return text(validate=validator, **common_params, **kwargs).execute()
    
    raise ValueError(f"Unsupported input_type: {input_type}")

def get_confirm(message, default=True, style=DEFAULT_STYLE, **kwargs):
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
