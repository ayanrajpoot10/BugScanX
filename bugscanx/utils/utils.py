import os
import pyfiglet
import ipaddress
from rich import print
from rich.text import Text
from InquirerPy import inquirer, get_style
from prompt_toolkit.validation import Validator, ValidationError

class UniversalValidator(Validator):
    VALIDATORS = {
        "required": lambda self, t: t or self._error("required"),
        "is_file": lambda self, t: os.path.isfile(t) or self._error("is_file"),
        "is_cidr": lambda self, t: self._validate_cidr(t),
        "is_digit": lambda self, t: self._validate_digits(t),
        "in_choices": lambda self, t: t in self.choices or self._error("in_choices"),
        "min": lambda self, t: self._validate_min(t),
        "max": lambda self, t: self._validate_max(t),
    }

    def __init__(self, rules=None, errors=None, **kwargs):
        super().__init__()
        self.rules = rules or {}
        self.errors = errors or {}
        self.choices = kwargs.get("choices", [])
        self.min = kwargs.get("min")
        self.max = kwargs.get("max")

    def _error(self, key, *args):
        message = self.errors.get(key, "Invalid input")
        if args:
            message = message.format(*args)
        raise ValidationError(message=message, cursor_position=len(self.document.text))

    def _validate_cidr(self, text):
        parts = [p.strip() for p in text.split(',') if p.strip()]
        if not parts:
            self._error("is_cidr", "empty input")
            
        for part in parts:
            try:
                ipaddress.ip_network(part, strict=False)
            except ValueError:
                self._error("is_cidr", part)

    def _validate_digits(self, text):
        parts = [p.strip() for p in text.split(',')] if text else []
        
        for part in parts:
            if not part.isdigit():
                self._error("is_digit", part)

    def _validate_min(self, text):
        if self.min is not None:
            num = int(text)
            if num < self.min:
                self._error("min", text, self.min)

    def _validate_max(self, text):
        if self.max is not None:
            num = int(text)
            if num > self.max:
                self._error("max", text, self.max)

    def validate(self, document):
        self.document = document
        text = document.text.strip()
        for rule in self.rules:
            self.VALIDATORS[rule](self, text)

style = get_style({"question": "#00ffff", "answer": "#00ffff", "questionmark": "#00ffff"}, style_override=False)

def get_input(
    message,
    input_type="text",
    default=None,
    rules=None,
    errors=None,
    choices=None,
    multiselect=False,
    transformer=None,
    min_value=None,
    max_value=None,
    only_files=True,
    style=style,
    qmark="➡️",
    amark="",
    newline_before=False,
    validate_input=True,
    use_async=False,
    **kwargs
):
    if newline_before:
        qmark = "\n" + qmark

    message += ":"
    execute_method = "execute_async" if use_async else "execute"

    if input_type == "choice":
        if choices is None:
            raise ValueError("'choices' must be provided for input_type 'choice'")
        return getattr(inquirer.select(
            message=message,
            choices=choices,
            default=default,
            multiselect=multiselect,
            transformer=transformer,
            qmark=qmark,
            amark=amark,
            style=style,
            **kwargs
        ), execute_method)()
    elif input_type == "file":
        rules = rules or ["required", "is_file"]
        errors = errors or {
            "required": "Input cannot be empty",
            "is_file": "Input is not a valid file path"
        }
        only_files = kwargs.pop('only_files', True)
        return getattr(inquirer.filepath(
            message=message,
            validate=UniversalValidator(rules=rules, errors=errors),
            default=str(default) if default is not None else "",
            only_files=only_files,
            qmark=qmark,
            amark=amark,
            style=style,
            **kwargs
        ), execute_method)()
    elif input_type == "number":
        rules = rules or ["required", "is_digit"]
        if min_value is not None and "min" not in rules:
            rules.append("min")
        if max_value is not None and "max" not in rules:
            rules.append("max")
        
        errors = errors or {}
        default_errors = {
            "required": "Input cannot be empty",
            "is_digit": "'{}' is not a number",
            "min": f"'{{}}' is less than the minimum allowed value of {min_value}" if min_value else "",
            "max": f"'{{}}' is greater than the maximum allowed value of {max_value}" if max_value else "",
        }
        for key, value in default_errors.items():
            if key not in errors and value:
                errors[key] = value
        
        validator = UniversalValidator(
            rules=rules,
            errors=errors,
            min=min_value,
            max=max_value
        )
        return getattr(inquirer.text(
            message=message,
            validate=validator,
            default=str(default) if default is not None else "",
            qmark=qmark,
            amark=amark,
            style=style,
            **kwargs
        ), execute_method)()
    elif input_type == "text":
        validator = None
        if validate_input:
            rules = rules or ["required"]
            errors = errors or {"required": "Input cannot be empty"}
            validator = UniversalValidator(rules=rules, errors=errors)
        
        return getattr(inquirer.text(
            message=message,
            validate=validator,
            default=str(default) if default is not None else "",
            qmark=qmark,
            amark=amark,
            style=style,
            **kwargs
        ), execute_method)()
    else:
        raise ValueError(f"Unsupported input_type: {input_type}")

def get_confirm(message, default=True, style=style, use_async=False, **kwargs):
    return getattr(inquirer.confirm(
        message=message,
        default=default,
        qmark="",
        amark="",
        style=style,
        **kwargs
    ), "execute_async" if use_async else "execute")()

def banner():
    banner_text = """
    [bold red]╔╗[/bold red] [turquoise2]╦ ╦╔═╗╔═╗╔═╗╔═╗╔╗╔═╗ ╦[/turquoise2]
    [bold red]╠╩╗[/bold red][turquoise2]║ ║║ ╦╚═╗║  ╠═╣║║║╔╩╦╝[/turquoise2]
    [bold red]╚═╝[/bold red][turquoise2]╚═╝╚═╝╚═╝╚═╝╩ ╩╝╚╝╩ ╚═[/turquoise2]
     [bold magenta]Dᴇᴠᴇʟᴏᴘᴇʀ: Aʏᴀɴ Rᴀᴊᴘᴏᴏᴛ
      Tᴇʟᴇɢʀᴀᴍ: @BᴜɢSᴄᴀɴX[/bold magenta]
    """
    print(banner_text)

def text_ascii(text, font="doom", color="white", shift=2):
    ascii_banner = pyfiglet.figlet_format(text, font=font)
    shifted_banner = "\n".join((" " * shift) + line for line in ascii_banner.splitlines())
    banner_text = Text(shifted_banner, style=color)
    print(banner_text)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
