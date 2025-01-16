import os
import pyfiglet
import ipaddress
from rich.text import Text
from rich.console import Console
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from InquirerPy import prompt

console = Console()

SUBSCAN_TIMEOUT = 5
SUBFINDER_TIMEOUT = 10

EXCLUDE_LOCATIONS = ["https://jio.com/BalanceExhaust", "http://filter.ncell.com.np/nc"]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def text_ascii(text, font="doom", color="white", shift=2):
    try:
        ascii_banner = pyfiglet.figlet_format(text, font=font)
        shifted_banner = "\n".join((" " * shift) + line for line in ascii_banner.splitlines())
        banner_text = Text(shifted_banner, style=color)
        console.print(banner_text)
    except pyfiglet.FontNotFound:
        pass

class UniversalValidator(Validator):
    def __init__(self, error_messages=None, validators=None):
        self.error_messages = error_messages or {}
        self.validators = validators or {}

    def validate(self, document):
        text = document.text.strip()
        for validator, value in self.validators.items():
            if validator == "not_empty" and not text:
                self._raise_validation_error("not_empty", "Input cannot be empty.", 0)
            elif validator == "is_digit":
                self._validate_digit(text)
            elif validator == "file_path" and not os.path.isfile(text):
                self._raise_validation_error("file_path", "File path is invalid or file does not exist.", 0)
        if "cidr" in self.validators:
            self._validate_cidr(text)
        if "choice" in self.validators:
            self._validate_choice(text)

    def _raise_validation_error(self, validator, default_message, cursor_position):
        raise ValidationError(
            message=self.error_messages.get(validator, default_message),
            cursor_position=cursor_position
        )

    def _validate_digit(self, text):
        values = text.split(',')
        for value in values:
            value = value.strip()
            if not value.isdigit():
                self._raise_validation_error("is_digit", "Each input must be a number.", 0)
            num_value = int(value)
            min_value = self.validators.get("min_value")
            max_value = self.validators.get("max_value")
            if min_value is not None and num_value < min_value:
                self._raise_validation_error("min_value", f"Each input must be at least {min_value}.", 0)
            if max_value is not None and num_value > max_value:
                self._raise_validation_error("max_value", f"Each input must be at most {max_value}.", 0)

    def _validate_cidr(self, text):
        values = text.split(',')
        for value in values:
            value = value.strip()
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError:
                self._raise_validation_error("cidr", "Each input must be a valid CIDR block.", 0)

    def _validate_choice(self, text):
        choices = self.validators["choice"]
        if text not in choices:
            self._raise_validation_error("choice", f"Input must be one of the following: {', '.join(choices)}", 0)

def get_input(prompt: str, default: str = None, validator=None, completer=None, multiline: bool = False):
    default = default or ""
    style = Style.from_dict({
        'prompt': 'cyan',
        'default': 'gray italic',
        'input': 'bold',
        'error': 'bg:#ff0000 #ffffff',
    })
    session = PromptSession()
    full_prompt = [('class:prompt', prompt), ('class:prompt', ': ')]
    try:
        response = session.prompt(
            full_prompt,
            default=default,
            completer=completer,
            validator=validator,
            validate_while_typing=True,
            multiline=multiline,
            style=style,
        )
        return response.strip() if response.strip() else default
    except ValidationError as e:
        print(f"\n{style['error']}{e.message}{style['error']}")
        return None
    except KeyboardInterrupt:
        print("\n Operation cancelled by the user.")
        return None

def get_txt_files_completer():
    txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
    return WordCompleter(txt_files, ignore_case=True)

completer = get_txt_files_completer()

def create_validator(error_messages, validators):
    return UniversalValidator(error_messages=error_messages, validators=validators)

not_empty_validator = create_validator(
    error_messages={"not_empty": "Input cannot be empty."},
    validators={"not_empty": True}
)

digit_validator = create_validator(
    error_messages={"not_empty": "Input cannot be empty.", "is_digit": "Input must be a number."},
    validators={"not_empty": True, "is_digit": True}
)

file_path_validator = create_validator(
    error_messages={"not_empty": "Input cannot be empty.", "file_path": "File path is invalid or file does not exist."},
    validators={"not_empty": True, "file_path": True}
)

cidr_validator = create_validator(
    error_messages={"not_empty": "Input cannot be empty.", "cidr": "Invalid CIDR block."},
    validators={"not_empty": True, "cidr": True}
)

choice_validator = create_validator(
    error_messages={"not_empty": "Input cannot be empty.", "choice": "Invalid choice."},
    validators={"not_empty": True, "choice": ["1", "2"]}
)

def create_digit_range_validator(min_value, max_value):
    return create_validator(
        error_messages={
            "not_empty": "Input cannot be empty.",
            "is_digit": "Input must be a number.",
            "min_value": f"Input must be at least {min_value}.",
            "max_value": f"Input must be at most {max_value}."
        },
        validators={
            "not_empty": True,
            "is_digit": True,
            "min_value": min_value,
            "max_value": max_value
        }
    )

digit_range_validator = create_digit_range_validator(min_value=1, max_value=12)

def create_prompt(prompt_type, message, name, **kwargs):
    question = {
        "type": prompt_type,
        "message": message,
        "name": name,
        "validate": lambda answer: 'You must choose at least one option.' if not answer else True
    }
    question.update(kwargs)
    
    answers = prompt([question])
    return answers.get(name, None)
