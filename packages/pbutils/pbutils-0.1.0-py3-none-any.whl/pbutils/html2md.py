import re

import markdownify
from loguru import logger

ReplacePattern = tuple[re.Pattern, str]

PATTERNS = [
    (re.compile(r"^\+ ", flags=re.MULTILINE), "    * "),
    (re.compile(r"^- ", flags=re.MULTILINE), "        * "),
]


def _apply_re_sub(patterns: list[ReplacePattern], text: str) -> str:
    for pattern, rep in patterns:
        text = re.sub(pattern, rep, text)
    return text


def html2md(html: bytes) -> str:
    md = markdownify.markdownify(html, strip=["b"])
    logger.debug(f"{md=}")
    ret = _apply_re_sub(patterns=PATTERNS, text=md)
    ret = "\n".join([line.rstrip() for line in ret.splitlines()]).strip()
    return ret
