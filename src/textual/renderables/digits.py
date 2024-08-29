from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType

from pkgutil import get_data as LoadGlyphs
import json
import math
#from textual import log
#log("stuff")


class Digits:
    """Renders a wXh unicode glyph 'font' for input token charactes.

    Args:
        text: Text to display.
        style: Style to apply to the digits.

    """

    height = 3
    width = 3

    def __init__(self, text: str, style: StyleType = "" ) -> None:
        self._text = text
        self._style = style
        self.load_glyphs()

    def set_face(self, Face="seven_segment", Family="box/sans") -> None:
        Font = 'renderables/glyphs/'
        Font += Family+"/"
        Font += Face+".json"
        return Font

    #def load_glyphs(self, Face: str="basic_latin", Family: str="box/sans") -> None:
    def load_glyphs(self, Face="seven_segment", Family="box/sans") -> None:
        glyph_faces = LoadGlyphs('textual', self.set_face(Face, Family) )
        self.GLYPHS = json.loads( glyph_faces )
        fallback = self.GLYPHS.get('block', Face).replace(" ", "_")
        if fallback != Face:
            back_faces = LoadGlyphs('textual', self.set_face(fallback, Family) )
            faces = json.loads( back_faces )
            if faces:
                for key in faces['character'].keys():
                    if key not in self.GLYPHS['character']:
                        self.GLYPHS['character'][key] = faces['character'][key]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        style = console.get_style(self._style)
        yield from self.render(style)

    def en_glyph(self, text: str, style: Style) -> RenderResult:
        """Engine to layout glyph strings in supercell with style

        Args:
            text: Text to display.
            style: Rich Style.

        Returns:
            2D list of glyph strings.
        """

        try:
            bbox_height = self.GLYPHS['fixed lines']
            bbox_width = self.GLYPHS['fixed columns']
            bbox_align = self.GLYPHS['align']
            bbox_tracking = self.GLYPHS['tracking']
            bbox_monospace = self.GLYPHS['monospace']
            faces_data = self.GLYPHS['character']
        except:
            raise Exception("missing required glyph face data")

        last_token = " "
        g_strings: list[list[str]] =[[] for i in range(1, bbox_height+1)]

        for token in text:
            if ord( token ) > 32 and ord( token ) < 127:
                default = {"glyph":["┌┬┐","├"+token+"┤","└┴┘"]}
            else:
                index = "{0:04x}".format( ord(token) )
                default = {"glyph":[index[0]+"┬"+index[1],"├ ┤",index[2]+"┴"+index[3]]}
            face = faces_data.get(token, default)
            Thint = face.get('tracking', bbox_tracking)
            bbox_apairs = self.GLYPHS.get('adjacent pairs',[])
            Mhint = face.get('monospace', bbox_monospace)
            Hhint = face.get('lines', bbox_height)
            Whint = face.get('columns', bbox_width)
            Ahint = face.get('align', bbox_align)
            glyph = face.get('glyph', face )
            if isinstance( glyph, dict ):
                if style.bold:
                    glyph = glyph.get('bold', glyph )
                else:
                    glyph = glyph.get('normal', glyph )

            #determine horizontal glyph placement in supercell
            if Mhint:
                if Ahint[0] == "left":
                    l_pad = 0
                    r_pad = bbox_width - Whint
                elif Ahint[0] == "right":
                    l_pad = bbox_width - Whint
                    r_pad = 0
                else:
                    pad = (bbox_width - Whint)/2.0
                    if last_token == " ":
                        l_pad = math.ceil(pad)
                        r_pad = math.floor(pad)
                    else:
                        l_pad = math.floor(pad)
                        r_pad = math.ceil(pad)
            else:
                l_pad = r_pad = 0

            #determine horizontal kerning and tracking adjustment
            if last_token+token not in bbox_apairs and Thint > 0:
                last_face = faces_data.get(last_token, {})
                Khint = face.get('kerning', True)
                last_Khint = last_face.get('kerning', True)
                last_Whint = last_face.get('columns', bbox_width)
                if last_Khint and Khint:
                    wedge = math.ceil( Thint )
                else:
                    wedge = math.ceil( Thint - last_Whint )
                if wedge > 0:
                    if Ahint[0] == "left":
                        r_pad += wedge
                    else:
                        l_pad += wedge

            #determine vertical glyph placement in supercell
            if Hhint == bbox_height:
                t_pad = b_pad = 0
            else:
                if Ahint[1] == "top":
                    t_pad = 0
                    b_pad = bbox_height - Hhint
                elif Ahint[1] == "bottom":
                    t_pad = bbox_height - Hhint
                    b_pad = 0
                else:
                    pad = (bbox_height - Hhint)/2.0
                    t_pad = math.ceil(pad)
                    b_pad = math.floor(pad)

            #construct glyph supercell sequence
            for n, g_row in enumerate( g_strings ):
                if n < t_pad or n >= t_pad+Hhint:
                    g_spot = " "*Whint
                else:
                    g_spot = glyph[n - t_pad] 
                g_row.append( " "*l_pad + g_spot + " "*r_pad )

            last_token = token
            #process next token or loop finished

        self.height = len( g_strings )
        self.width = len( g_strings[0] )
        return g_strings

    def render(self, style: Style) -> RenderResult:
        """Render with the given style

        Args:
            style: Rich Style.

        Returns:
            Result of render.
        """
        for g_row in self.en_glyph( self._text, style):
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
        return cls.height

    @classmethod
    def get_width(cls, text: str) -> int:
        """Calculate the width without rendering.

        Args:
            text: Text which may be displayed in the `Digits` widget.

        Returns:
            width of the text (in cells).
        """
        return cls.width

    def __rich_measure__(
        self, console: Console, options: ConsoleOptions
    ) -> Measurement:
        width = self.get_width(self._text)
        return Measurement(width, width)
