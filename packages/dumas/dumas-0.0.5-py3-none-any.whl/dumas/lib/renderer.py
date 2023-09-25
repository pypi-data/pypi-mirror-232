import re
from pathlib import Path

from marko import Markdown, block
from marko.md_renderer import MarkdownRenderer

from dumas.lib.interpreters import interpreters


FENCED_CODE_LANG_REGEX = re.compile(r"dumas\[(?P<interpreter_name>[\d\w_]+)(@(?P<interpreter_id>[\w\d_-]+))?\]")


class RenderError(Exception):
    def __init__(self, msg, element, raw):
        super().__init__(msg)
        self.element = element
        self.raw = raw


class Renderer(MarkdownRenderer):
    def __init__(self):
        super().__init__()

    def render_fenced_code(self, element: block.FencedCode) -> str:
        match = FENCED_CODE_LANG_REGEX.match(element.lang)

        if not match:
            return super().render_fenced_code(element)

        match_dict = match.groupdict()
        interpreter_id = match_dict.get("interpreter_id", "default")
        interpreter_name = match_dict["interpreter_name"]

        interpreter = interpreters[interpreter_name](interpreter_id)

        try:
            result = [self.render(r) for r in interpreter.run(self.render_raw_text(element.children[0]), **{})]
        except Exception as e:
            raise RenderError(
                f"Fail to process element \n{super().render_fenced_code(element)}",
                element,
                raw=super().render_fenced_code(element),
            ) from e

        return "".join(result)


def render_text(text, *, renderer=Renderer) -> str:
    return Markdown(renderer=renderer)(text)


def render_file(path_to_file: Path, *, renderer=Renderer) -> str:
    try:
        return render_text(path_to_file.read_text(), renderer=renderer)
    except RenderError as e:
        raise RenderError(
            f"Fail to process file {path_to_file}'s element \n{e.raw}", element=e.element, raw=e.raw
        ) from None
