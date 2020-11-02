# encoding: utf-8
import re

save_char_map = {
    'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
    ' ': '_', '.': '_', ',': '_', ':': '_'
}


def get_legal_character(char, allow=""):
    if re.match("[a-zA-Z_0-9{}]".format(allow), char):
        return char
    else:
        return save_char_map.get(char, "_")


def hash_iterator(name_pattern, start=1, step=1, hashlen=3):
    parts = re.split("#+", name_pattern)
    if len(parts) > 1:
        hashlen = len(re.search("#+", name_pattern).group())
    else:
        parts.append("")
    while True:
        yield "".join(
            [parts[0], str(start).zfill(hashlen)] + parts[1:]
        )
        start += step
