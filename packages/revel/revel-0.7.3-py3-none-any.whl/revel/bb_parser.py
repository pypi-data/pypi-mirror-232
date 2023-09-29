import re
from typing import *  # type: ignore

from . import style

__all__ = [
    "escape",
    "unescape",
]

BBCODE_TAG_PATTERN = re.compile(r"(?<!\[)(\[\[)*(\[/?[\w\- ]*\])")


BBCODE_STYLES = {
    "bold": (style.Format.BOLD, style.Format.RESET_BOLD),
    "dim": (style.Format.DIM, style.Format.RESET_DIM),
    "italic": (style.Format.ITALIC, style.Format.RESET_ITALIC),
    "underlined": (style.Format.UNDERLINED, style.Format.RESET_UNDERLINED),
    "inverted": (style.Format.INVERTED, style.Format.RESET_INVERTED),
    "strikethrough": (style.Format.STRIKETHROUGH, style.Format.RESET_STRIKETHROUGH),
    "black": (style.Fore.BLACK, style.Fore.RESET),
    "red": (style.Fore.RED, style.Fore.RESET),
    "green": (style.Fore.GREEN, style.Fore.RESET),
    "yellow": (style.Fore.YELLOW, style.Fore.RESET),
    "blue": (style.Fore.BLUE, style.Fore.RESET),
    "magenta": (style.Fore.MAGENTA, style.Fore.RESET),
    "cyan": (style.Fore.CYAN, style.Fore.RESET),
    "white": (style.Fore.WHITE, style.Fore.RESET),
    "bg-black": (style.Back.BLACK, style.Back.RESET),
    "bg-red": (style.Back.RED, style.Back.RESET),
    "bg-green": (style.Back.GREEN, style.Back.RESET),
    "bg-yellow": (style.Back.YELLOW, style.Back.RESET),
    "bg-blue": (style.Back.BLUE, style.Back.RESET),
    "bg-magenta": (style.Back.MAGENTA, style.Back.RESET),
    "bg-cyan": (style.Back.CYAN, style.Back.RESET),
    "bg-white": (style.Back.WHITE, style.Back.RESET),
}


def prepare_plaintext_highlights() -> (
    Tuple[
        re.Pattern,
        Dict[str, Tuple[str, str]],
    ]
):
    raw = (
        (
            "url",
            r"\bhttps?://[^\s/$.?#].[^\s]*\b",
            style.Fore.BLUE + style.Format.UNDERLINED,
            style.Fore.RESET + style.Format.RESET_UNDERLINED,
        ),
        (
            "email",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            style.Fore.BLUE,
            style.Fore.RESET,
        ),
        (
            "number",
            r"[+-]?\d*([.,_]\d*)+(?:[eE][+-]?(?:\d*([.,_]\d*)*))?",
            style.Fore.GREEN,
            style.Fore.RESET,
        ),
    )

    # Create a combined pattern. Make sure to assign the name to each capture
    # group
    combined_pattern = "|".join(
        [f"(?P<{name}>{pattern})" for name, pattern, _, _ in raw]
    )

    # Create a mapping of names to styles
    styles: Dict[str, Tuple[str, str]] = {
        name: (prefix, suffix) for name, _, prefix, suffix in raw
    }

    return re.compile(combined_pattern), styles


(
    PLAINTEXT_HIGHLIGHT_PATTERN,
    PLAINTEXT_HIGHLIGHT_STYLES,
) = prepare_plaintext_highlights()


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

    # Highlight some common plaintext patterns
    def replacement(match):
        # Find the name of the capture group that matched
        for name, value in match.groupdict().items():
            if value is not None:
                prefix, suffix = PLAINTEXT_HIGHLIGHT_STYLES[name]
                break
        else:
            assert False, "Unreachable"

        return prefix + value + suffix

    return re.sub(PLAINTEXT_HIGHLIGHT_PATTERN, replacement, text)


def process_bbcode(text: str) -> Iterable[str]:
    """
    Parses and applies BBCode markup to a string. The resulting strings should
    be concatenated to form the final output.
    """

    # The index in the input string of the end of the previous match
    previous_end = 0

    # All currently active styles. Each [tag] corresponds to one entry. This is
    # a list of lists, because a single tag can contain multiple styles:
    #
    # [bold red]
    style_stack: List[List[str]] = []

    # Find all matches using the precompiled pattern
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

        # Closing tag
        if span.startswith("[/"):
            # It's okay not to specify any styles: [/]
            #
            # If that's the case, close the most recent style(s)
            try:
                styles = style_stack.pop()
            except IndexError:
                pass
            else:
                # Yield the closing tags
                for style in styles:
                    try:
                        open_style, close_style = BBCODE_STYLES[style]
                    except KeyError:
                        pass
                    else:
                        yield close_style

        # Opening tag
        else:
            styles = span[1:-1].split()
            style_stack.append(styles)

            # Apply the styles
            for style in styles:
                try:
                    open_style, close_style = BBCODE_STYLES[style]
                except KeyError:
                    pass
                else:
                    yield open_style

    # Yield the remaining text
    remainder = text[previous_end:]

    if remainder:
        yield _process_plain_text(remainder)

    # Close any remaining styles
    #
    # This could be done using a single reset code, but that wouldn't allow
    # concatenating multiple markup strings together.
    for styles in style_stack:
        for style in styles:
            try:
                open_style, close_style = BBCODE_STYLES[style]
            except KeyError:
                pass
            else:
                yield close_style


def unescape(value: Any) -> Any:
    """
    Applies BBCode markup to a string.
    """
    # Make sure the value is a string
    value = str(value)

    # Process the string
    return "".join(process_bbcode(value))
