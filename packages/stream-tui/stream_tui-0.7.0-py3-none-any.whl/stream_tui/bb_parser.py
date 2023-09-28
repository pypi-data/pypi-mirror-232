import re
from typing import *  # type: ignore

__all__ = [
    "escape",
    "unescape",
]

BBCODE_TAG_PATTERN = re.compile(r"(?<!\[)(\[\[)*(\[/?[\w-]+\])")


BBCODE_STYLES = {
    "bold": ("\033[1m", "\033[22m"),
    "dim": ("\033[2m", "\033[22m"),
    "italic": ("\033[3m", "\033[23m"),
    "underlined": ("\033[4m", "\033[24m"),
    "inverted": ("\033[7m", "\033[27m"),
    "strikethrough": ("\033[9m", "\033[29m"),
    "black": ("\033[30m", "\033[39m"),
    "red": ("\033[31m", "\033[39m"),
    "green": ("\033[32m", "\033[39m"),
    "yellow": ("\033[33m", "\033[39m"),
    "blue": ("\033[34m", "\033[39m"),
    "magenta": ("\033[35m", "\033[39m"),
    "cyan": ("\033[36m", "\033[39m"),
    "white": ("\033[37m", "\033[39m"),
    "bg-black": ("\033[40m", "\033[49m"),
    "bg-red": ("\033[41m", "\033[49m"),
    "bg-green": ("\033[42m", "\033[49m"),
    "bg-yellow": ("\033[43m", "\033[49m"),
    "bg-blue": ("\033[44m", "\033[49m"),
    "bg-magenta": ("\033[45m", "\033[49m"),
    "bg-cyan": ("\033[46m", "\033[49m"),
    "bg-white": ("\033[47m", "\033[49m"),
}


def escape(value: Any) -> str:
    """
    Escapes a string to prevent BBCode from being interpreted.
    """
    # Make sure the value is a string
    value = str(value)

    # Double up brackets
    return value.replace("[", "[[")


def _process_plain_text(text: str) -> str:
    # Remove any double brackets
    text = text.replace("[[", "[")

    # TODO: Highlight numbers, emails, urls, whatever makes sense

    return text


def preprocess_bbcode(text: str) -> Iterable[str]:
    """
    Given a BBCode string, split it into BBCode sections. Each section is either
    an opening tag, a closing tag, or a plain text string.
    """

    current_styles: Set[str] = set()

    # Find all matches using the precompiled pattern
    previous_end = 0

    for match in BBCODE_TAG_PATTERN.finditer(text):
        # Get the matching region
        start_index = match.start(2)
        end_index = match.end(2)
        span = text[start_index:end_index]

        assert span.startswith("["), (span, start_index, end_index, match.groups())

        # Anything up to that region is plain text
        if start_index > 0:
            yield _process_plain_text(text[previous_end:start_index])

        previous_end = end_index

        # Closing tag?
        if span.startswith("[/"):
            # Get the tag name
            tag_name = span[2:-1]

            # This style is no longer active
            current_styles.discard(tag_name)

            # Yield the closing tag
            try:
                open_style, close_style = BBCODE_STYLES[tag_name]
            except KeyError:
                pass
            else:
                yield close_style

        # Opening tag
        else:
            tag_name = span[1:-1]

            # Apply the style
            try:
                open_style, close_style = BBCODE_STYLES[tag_name]
            except KeyError:
                pass
            else:
                yield open_style

                # This style is now active
                current_styles.add(tag_name)

    # Yield the remaining text
    remainder = text[previous_end:]

    if remainder:
        yield _process_plain_text(remainder)

    # Close any remaining styles
    yield "\033[0m"


def unescape(value: Any) -> Any:
    """
    Unescapes BBCode markup from a string.
    """
    # Make sure the value is a string
    value = str(value)

    # Process the string
    return "".join(preprocess_bbcode(value))
