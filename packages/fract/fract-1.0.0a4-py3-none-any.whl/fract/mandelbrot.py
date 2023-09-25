from contextlib import contextmanager
from multiprocessing import cpu_count
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator

from fract.mandelbrot_calculator import MandelbrotCalculator


@contextmanager
def mandelbrot_calculator(
    calculators: int | None = None,
    exporters: int = 1,
) -> Iterator[MandelbrotCalculator]:
    if calculators is None:
        # Keep a core free for our fellow programs.
        calculators = cpu_count() - exporters - 1

    with TemporaryDirectory() as pool_working_directory:
        with MandelbrotCalculator(
            calculators,
            exporters,
            Path(pool_working_directory),
        ) as pool:
            yield pool
