import pytest
from pyturtle.shapes.line import Line


class TurtleMock:
    def __init__(self):
        self.penup_called = False
        self.pendown_called = False
        self.goto_called_with = []

    def penup(self):
        self.penup_called = True

    def pendown(self):
        self.pendown_called = True

    def goto(self, x, y):
        self.goto_called_with.append((x, y))


def test_line_draw():
    # Create an instance of Line
    turtle = TurtleMock()
    steps = 10
    x1 = 0
    y1 = 0
    x2 = 100
    y2 = 100
    line = Line(turtle=turtle, steps=steps, x1=x1, y1=y1, x2=x2, y2=y2)

    # Call the draw method
    line.draw()

    # Assertions
    assert turtle.penup_called
    assert turtle.pendown_called
    assert (x1, y1) in turtle.goto_called_with
    assert (x2, y2) in turtle.goto_called_with
    assert len(line.coordinates) == 10
