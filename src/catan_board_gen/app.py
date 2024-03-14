"""
Generate random, balanced boards for the board game Catan
"""
import math 

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.fonts import SANS_SERIF
from toga.constants import Baseline
from toga.colors import WHITE, rgb


class BalancedCatanBoardGenerator(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        self.main_window = toga.MainWindow(title=self.formal_name)

        self.canvas = toga.Canvas(
            style=Pack(flex=1),
            on_resize=self.on_resize,
            on_press=self.on_press,
        )

        self.label1 = toga.Label("Label 1")
        self.label2 = toga.Label("Label 2")

        main_box = toga.Box(children=[self.canvas, self.label1, self.label2])

        self.main_window.content = main_box

        self.draw()

        self.main_window.show()

    def draw_text(self):
        font = toga.Font(family=SANS_SERIF, size=20)
        self.text_width, text_height = self.canvas.measure_text("Tiberius", font)

        x = (150 - self.text_width) // 2
        y = 175

        with self.canvas.Stroke(color="REBECCAPURPLE", line_width=4.0) as rect_stroker:
            self.text_border = rect_stroker.rect(
                x - 5,
                y - 5,
                self.text_width + 10,
                text_height + 10,
            )

        with self.canvas.Fill(color=rgb(149, 119, 73)) as text_filler:
            self.text = text_filler.write_text("Test", x, y, font, Baseline.TOP)

    def draw(self):
        with self.canvas.Stroke(line_width=4.0) as stroker:
            with stroker.ClosedPath(112, 103) as path:
                path.line_to(112, 113)
                path.ellipse(73, 114, 39, 47, 0, 0, math.pi)
        self.draw_text()


    def on_resize(self, widget, width, height, **kwargs):
        if widget.context:
            left_pad = (width - self.text_width) //2
            self.text.x = left_pad
            self.text_border.x = left_pad - 5
            widget.redraw()
#            self.main_window.info_dialog("Hey!", f"resized to {width} x {height}")

    def on_press(self, widget, x, y, **kwargs):
        self.main_window.info_dialog("Hey!", f"Pressed at ({x}, {y})")

def main():
    return BalancedCatanBoardGenerator()

