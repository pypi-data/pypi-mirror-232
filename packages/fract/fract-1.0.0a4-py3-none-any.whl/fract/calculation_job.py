from typing import TypedDict

from fract.to_color import ToColor


class CalculationJob(TypedDict):
    imaginary_span: float
    min_imaginary: float
    min_real: float
    max_iterations: int
    pixel_height: int
    pixel_width: int
    real_span: float
    to_color: ToColor
    working_directory: str
    y: int
