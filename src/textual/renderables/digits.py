from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType
from pkgutil import get_data as LoadGlyphs
import json
import math

DIGITS = " 0123456789+-^x:"
DIGITS3X3 = """\



┏━┓
┃ ┃
┗━┛
 ┓
 ┃
╺┻╸
╺━┓
┏━┛
┗━╸
╺━┓
 ━┫
╺━┛
╻ ╻
┗━┫
  ╹
┏━╸
┗━┓
╺━┛
┏━╸
┣━┓
┗━┛
╺━┓
  ┃
  ╹
┏━┓
┣━┫
┗━┛
┏━┓
┗━┫
╺━┛

╺╋╸


╺━╸

 ^



 ×


 :

""".splitlines()


class Digits:
    """Renders a 3X3 unicode 'font' for numerical values.

    Args:
        text: Text to display.
        style: Style to apply to the digits.

    """

    def __init__(self, text: str, style: StyleType = "") -> None:
        self._text = text
        self._style = style


    font = "box/sans/default.json"
    glyph_faces = LoadGlyphs('textual' , 'renderables/glyphs/' + font )
    GLYPHS = json.loads( glyph_faces )

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        style = console.get_style(self._style)
        yield from self.render(style)

    def get_glyph(self, token: str) -> None:
        my_glyph = self.GLYPHS['character'][ token ]['glyph']
        try:
            my_glyph = my_glyph['bold']
        except:
            pass
        return my_glyph
            

    def render(self, style: Style) -> RenderResult:
        """Render with the given style

        Args:
            style: Rich Style.

        Returns:
            Result of render.
        """
        monospace = True
        was_space = True

        try:
            bbox_height = self.GLYPHS['fixed lines']
            bbox_width = self.GLYPHS['fixed columns']
            bbox_align = self.GLYPHS['fixed align']
            faces_data = self.GLYPHS['character']
        except:
            raise Exception("missing required glyph face data")

        g_strings: list[list[str]] =[[] for i in range(1, bbox_height+1)]

        for token in self._text:
            face = faces_data.get(token, token)
            Hhint = face.get('lines', bbox_height)
            Whint = face.get('columns', bbox_width)
            Ahint = face.get('align', bbox_align)
            face = face.get('glyph', face )
            if isinstance( face, dict ):
                face = face.get('bold', face )

            if Whint == bbox_width:
                l_pad = r_pad = 0
            else:
                if Ahint[0] == "left":
                    l_pad = 0
                    r_pad = bbox_width - Whint
                elif Ahint[0] == "right":
                    r_pad = 0
                    l_pad = bbox_width - Whint
                else:
                    pad = (bbox_width - Whint)/2.0
                    if was_space:
                        l_pad = math.ceil(pad)
                        r_pad = math.floor(pad)
                    else:
                        r_pad = math.ceil(pad)
                        l_pad = math.floor(pad)
            if token != " ":
                was_space = False
            else: 
                was_space = True

            if Hhint == bbox_height:
                t_pad = b_pad = 0
            else:
                if Ahint[1] == "top":
                    t_pad = 0
                    b_pad = bbox_height - Hhint
                elif Ahint[1] == "bottom":
                    b_pad = 0
                    t_pad = bbox_height - Hhint
                else:
                    pad = (bbox_height - Hhint)/2.0
                    t_pad = math.ceil(pad)
                    b_pad = math.floor(pad)

            for n, g_row in enumerate( g_strings ):
                if n < t_pad or n >= t_pad+Hhint:
                    g_row.append( " "*Whint )
                else:
                    g_row.append( " "*l_pad + face[n - t_pad] + " "*r_pad )

        for g_row in g_strings:
            yield Segment("".join(g_row), style)
            yield Segment.line()



    @classmethod
    def get_height(cls, text: str) -> int:
        """Calculate the width without rendering.

        Args:
            text: Text which may be displayed in the `Digits` widget.

        Returns:
            width of the text (in cells).
        """
        #Read from the max of default or tcss glyphs fixed height 
        height = 3
        return height

    @classmethod
    def get_width(cls, text: str) -> int:
        """Calculate the width without rendering.

        Args:
            text: Text which may be displayed in the `Digits` widget.

        Returns:
            width of the text (in cells).
        """
        width = sum(3 if character in DIGITS else 1 for character in text)
        return width

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        width = self.get_width(self._text)
        return Measurement(width, width)
