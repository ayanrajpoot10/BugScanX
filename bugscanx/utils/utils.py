import os
import ipaddress

import pyfiglet
from rich.console import Console
from rich.text import Text

from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.patch_stdout import patch_stdout

from InquirerPy import prompt

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    banner_text = """
    [bold red]╔╗[/bold red] [turquoise2]╦ ╦╔═╗╔═╗╔═╗╔═╗╔╗╔═╗ ╦[/turquoise2]
    [bold red]╠╩╗[/bold red][turquoise2]║ ║║ ╦╚═╗║  ╠═╣║║║╔╩╦╝[/turquoise2]
    [bold red]╚═╝[/bold red][turquoise2]╚═╝╚═╝╚═╝╚═╝╩ ╩╝╚╝╩ ╚═[/turquoise2]
     [bold magenta]Dᴇᴠᴇʟᴏᴘᴇʀ: Aʏᴀɴ Rᴀᴊᴘᴏᴏᴛ
      Tᴇʟᴇɢʀᴀᴍ: @BᴜɢSᴄᴀɴX[/bold magenta]
    """
    console.print(banner_text)

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
        
        self.validation_methods = {
            "not_empty": self._validate_not_empty,
            "is_digit": self._validate_digit,
            "file_path": self._validate_file_path,
            "cidr": self._validate_cidr,
            "choice": self._validate_choice,
        }

    def validate(self, document):
        text = document.text.strip()
        for validator in self.validators:
            if validator in self.validation_methods:
                self.validation_methods[validator](text)

    def _raise_error(self, key, message, pos=0):
        raise ValidationError(message=self.error_messages.get(key, message), cursor_position=pos)

    def _validate_not_empty(self, text):
        if not text:
            self._raise_error("not_empty", "Input cannot be empty.")

    def _validate_digit(self, text):
        values = map(str.strip, text.split(','))
        min_val, max_val = self.validators.get("min_value"), self.validators.get("max_value")

        for value in values:
            if not value.isdigit():
                self._raise_error("is_digit", "Each input must be a number.")
            num = int(value)
            if min_val is not None and num < min_val:
                self._raise_error("min_value", f"Each input must be at least {min_val}.")
            if max_val is not None and num > max_val:
                self._raise_error("max_value", f"Each input must be at most {max_val}.")

    def _validate_file_path(self, text):
        if not os.path.isfile(text):
            self._raise_error("file_path", "File path is invalid or file does not exist.")

    def _validate_cidr(self, text):
        for value in map(str.strip, text.split(',')):
            try:
                ipaddress.ip_network(value, strict=False)
            except ValueError:
                self._raise_error("cidr", "Each input must be a valid CIDR block.")

    def _validate_choice(self, text):
        if text not in self.validators.get("choice", []):
            self._raise_error("choice", f"Input must be one of: {', '.join(self.validators['choice'])}")

def get_input(prompt, default="", validator=None, completer=None):
    style = Style.from_dict({'prompt': 'cyan', 'input': 'bold'})
    session = PromptSession()
    try:
        with patch_stdout():
            return session.prompt([("class:prompt", f"{prompt}: ")], default=default, completer=completer,
                                  validator=validator, validate_while_typing=True, style=style).strip() or default
    except KeyboardInterrupt:
        print("\nOperation cancelled by the user.")
        return None

def get_txt_files_completer():
    return WordCompleter([f for f in os.listdir('.') if f.endswith('.txt')], ignore_case=True)

completer = get_txt_files_completer()

def create_validator(error_msgs, **validators):
    return UniversalValidator(error_messages=error_msgs, validators=validators)

not_empty_validator = create_validator({"not_empty": "Input cannot be empty."}, not_empty=True)
digit_validator = create_validator({"not_empty": "Input cannot be empty.", "is_digit": "Input must be a number."}, 
                                   not_empty=True, is_digit=True)
file_path_validator = create_validator({"not_empty": "Input cannot be empty.", "file_path": "File path is invalid."},
                                       not_empty=True, file_path=True)
cidr_validator = create_validator({"not_empty": "Input cannot be empty.", "cidr": "Invalid CIDR block."},
                                  not_empty=True, cidr=True)
choice_validator = create_validator({"not_empty": "Input cannot be empty.", "choice": "Invalid choice."},
                                    not_empty=True, choice=["1", "2"])
digit_range_validator = create_validator({
    "not_empty": "Input cannot be empty.", "is_digit": "Input must be a number.",
    "min_value": "Input must be at least 1.", "max_value": "Input must be at most 12."
}, not_empty=True, is_digit=True, min_value=1, max_value=12)

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
