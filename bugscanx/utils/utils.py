import os
from InquirerPy import get_style
from InquirerPy.prompts import ListPrompt as select
from InquirerPy.prompts import FilePathPrompt as filepath
from InquirerPy.prompts import InputPrompt as text
from InquirerPy.prompts import ConfirmPrompt as confirm

from .validators import create_validator, required, is_file, is_digit

DEFAULT_STYLE = get_style({"question": "#87CEEB", "answer": "#00FF7F", "answered_question": "#808080"}, style_override=False)

def get_input(
    message,
    input_type="text",
    default=None,
    validators=None,
    choices=None,
    multiselect=False,
    transformer=None,
    style=DEFAULT_STYLE,
    qmark="",
    amark="",
    validate_input=True,
    show_cursor=False,
    instruction="",
    long_instruction="",
    **kwargs
):
    message = f" {message}:"
    
    default_str = "" if default is None else str(default)
    
    common_params = {
        "message": message,
        "default": default_str,
        "qmark": qmark,
        "amark": amark,
        "style": style,
        "instruction": instruction,
        "long_instruction": long_instruction,
        **kwargs
    }

    if validators is None and validate_input:
        if input_type == "file":
            validators = [required, is_file]
        elif input_type == "number":
            validators = [required, is_digit]
        elif input_type == "text":
            validators = [required]
    
    validator = None
    if validators and validate_input:
        validator = create_validator(validators)

    if input_type == "choice":
        return select(
            choices=choices,
            multiselect=multiselect,
            transformer=transformer,
            show_cursor=show_cursor,
            **common_params
        ).execute()
    
    elif input_type == "file":
        only_files = kwargs.pop('only_files', True)
        return filepath(
            validate=validator,
            only_files=only_files,
            **common_params
        ).execute()
    
    elif input_type == "number" or input_type == "text":
        return text(
            validate=validator,
            **common_params
        ).execute()
    
    else:
        raise ValueError(f"Unsupported input_type: {input_type}")

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
