import os
from InquirerPy import get_style
from InquirerPy.prompts import (
    ListPrompt as select,
    FilePathPrompt as filepath,
    InputPrompt as text,
    ConfirmPrompt as confirm,
)
from .validators import create_validator, VALIDATORS


DEFAULT_STYLE = get_style(
    {
        "question": "#87CEEB",
        "answer": "#00FF7F",
        "answered_question": "#808080",
    },
    style_override=False,
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
    instruction="",
    mandatory=True,
    **kwargs
):
    def auto_strip(result):
        return result.strip() if isinstance(result, str) else result
    
    params = {
        "message": f" {message.strip()}" + (":" if not instruction else ""),
        "default": "" if default is None else str(default),
        "qmark": "",
        "amark": "",
        "style": style,
        "instruction": instruction + (":" if instruction else ""),
        "mandatory": mandatory,
        "transformer": transformer,
    }
    
    if validators:
        if isinstance(validators, str) and validators in VALIDATORS:
            params["validate"] = create_validator(*VALIDATORS[validators])
        elif isinstance(validators, (list, tuple)):
            params["validate"] = create_validator(*validators)
    
    if input_type == "choice":
        params.update({
            "choices": choices,
            "multiselect": multiselect,
            "show_cursor": kwargs.get("show_cursor", False),
        })
        return select(**params).execute()
    
    elif input_type == "file":
        params["only_files"] = kwargs.get("only_files", True)
        return auto_strip(filepath(**params).execute())
    
    else:
        return auto_strip(text(**params).execute())


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
