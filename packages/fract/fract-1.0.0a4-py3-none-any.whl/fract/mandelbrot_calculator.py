from __future__ import annotations

from datetime import datetime
from multiprocessing import Lock, Manager, Pool, Queue, current_process
from os.path import join
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp
from types import TracebackType
from typing import Iterator, Type

import png

from fract.calculation_job import CalculationJob
from fract.colors import to_greyscale
from fract.export_job import ExportJob
from fract.logging import logger
from fract.to_color import ToColor


class MandelbrotCalculator:
    def __init__(
        self,
        calculators: int,
        exporters: int,
        pool_working_directory: Path,
    ) -> None:
        self._started = datetime.now()

        self._calculators = calculators
        self._exporters = exporters
        self._pool_working_directory = pool_working_directory

        self._exports = Manager().dict()
        self._exports_lock = Lock()

        self._remaining = Manager().dict()
        self._remaining_lock = Lock()

        self._calculation_queue: "Queue[CalculationJob | None]" = Queue()
        self._export_queue: "Queue[str | None]" = Queue()

        logger.debug("Starting %i calculators", calculators)
        self._calculation_pool = Pool(
            calculators,
            self._start_calculation_worker,
            (self._calculation_queue, self._export_queue),
        )
        # Don't allow any more processes.
        self._calculation_pool.close()

        logger.debug("Starting %i exporters", exporters)
        self._export_pool = Pool(
            exporters,
            self._start_export_worker,
            (self._export_queue,),
        )
        # Don't allow any more processes.
        self._export_pool.close()

    def __enter__(self) -> MandelbrotCalculator:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_inst: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        for _ in range(self._calculators):
            self._calculation_queue.put(None)

        self._calculation_pool.join()

        for _ in range(self._exporters):
            self._export_queue.put(None)

        self._export_pool.join()

        logger.info(
            "%s closed after %0.1f seconds",
            self.__class__.__name__,
            (datetime.now() - self._started).total_seconds(),
        )

        return exc_type is not None

    def _start_calculation_worker(
        self,
        calculation_queue: "Queue[CalculationJob | None]",
        export_queue: "Queue[str | None]",
    ) -> None:
        try:
            self._start_calculation_worker_unsafe(
                calculation_queue,
                export_queue,
            )
        except Exception:
            logger.exception("Calculation failed.")
            raise

    def _start_calculation_worker_unsafe(
        self,
        calculation_queue: "Queue[CalculationJob | None]",
        export_queue: "Queue[str | None]",
    ) -> None:
        name = current_process().name
        logger.debug("Calculation worker %s started", name)

        while True:
            job = calculation_queue.get()

            if job is None:
                logger.debug("Calculation worker %s stopping", name)
                return

            y = job["y"]

            logger.debug("Calculation worker %s now working on line %i", name, y)

            pixel_height = job["pixel_height"]
            main_real = job["min_real"]
            min_imaginary = job["min_imaginary"]
            max_iterations = job["max_iterations"]
            working_directory = job["working_directory"]

            imaginary = min_imaginary + (y / pixel_height) * job["imaginary_span"]

            pixel_width = job["pixel_width"]

            path = join(working_directory, str(y))

            with open(path, "wb") as f:
                for x in range(pixel_width):
                    color = MandelbrotCalculator.calculate_color(
                        job["to_color"],
                        main_real + (x / pixel_width) * job["real_span"],
                        imaginary,
                        max_iterations,
                    )

                    f.write(color[0].to_bytes(16))
                    f.write(color[1].to_bytes(16))
                    f.write(color[2].to_bytes(16))

            with self._remaining_lock:
                remaining_count = self._remaining[working_directory] - 1
                if self._remaining[working_directory] == 0:
                    del self._remaining[working_directory]
                else:
                    self._remaining[working_directory] = remaining_count

            if remaining_count == 0:
                export_queue.put(working_directory)

    def _start_export_worker(self, queue: "Queue[str | None]") -> None:
        try:
            self._start_export_worker_unsafe(queue)
        except Exception:
            logger.exception("Export failed.")
            raise

    def _start_export_worker_unsafe(self, queue: "Queue[str | None]") -> None:
        name = current_process().name
        logger.debug("Export worker %s started", name)

        while True:
            working_directory = queue.get()

            if working_directory is None:
                logger.debug("Export worker %s stopping", name)
                return

            logger.debug(
                "Export worker %s received %s",
                name,
                working_directory,
            )

            with self._exports_lock:
                job = self._exports[working_directory]
                del self._exports[working_directory]

            path = job["path"]
            width = job["width"]
            height = job["height"]

            with open(path, "wb") as f:
                writer = png.Writer(
                    width,
                    height,
                    bitdepth=16,
                    greyscale=False,
                )

                rows = MandelbrotCalculator.iterations_to_color_rows(
                    height,
                    working_directory,
                )

                writer.write(f, rows)

            logger.info("Exported %s.", path)

            rmtree(working_directory)

    @staticmethod
    def calculate_color(
        to_color: ToColor,
        real: float,
        imaginary: float,
        maximum: int,
    ) -> tuple[int, int, int]:
        """
        Counts the number of iterations required for the point (`real`,
        `imaginary`) to escape the Mandelbrot set, to a `maximum` iteration.
        """

        count = 0

        if MandelbrotCalculator.estimate_in_mandelbrot_set(real, imaginary):
            count = maximum

        x = 0.0
        y = 0.0

        x_squared = 0.0
        y_squared = 0.0

        x_cycle = 0.0
        y_cycle = 0.0

        period = 0

        while x_squared + y_squared <= 4.0 and count < maximum:
            y = ((2 * x) * y) + imaginary
            x = (x_squared - y_squared) + real

            if x == x_cycle and y == y_cycle:
                count = maximum
                break

            x_squared = x * x
            y_squared = y * y

            period += 1

            if period > 20:
                period = 0
                x_cycle = x
                y_cycle = y

            count += 1

        return to_color(count, maximum)

    def enqueue(
        self,
        width: int,
        height: int,
        path: Path | str,
        to_color: ToColor | None = None,
        real: float = -0.65,
        imaginary: float = 0.0,
        real_span: float = 3.0,
        max_iterations: int = 1_000,
    ) -> None:
        working_directory = mkdtemp(dir=self._pool_working_directory)

        self._exports[working_directory] = ExportJob(
            height=height,
            path=path.as_posix() if isinstance(path, Path) else path,
            width=width,
        )

        self._remaining[working_directory] = height
        imaginary_span = real_span * (height / width)

        for y in range(height):
            job = CalculationJob(
                imaginary_span=imaginary_span,
                min_imaginary=imaginary - (imaginary_span / 2),
                min_real=real - (real_span / 2),
                max_iterations=max_iterations,
                pixel_height=height,
                pixel_width=width,
                real_span=real_span,
                to_color=to_color or to_greyscale,
                working_directory=working_directory,
                y=y,
            )

            self._calculation_queue.put(job)

    @staticmethod
    def estimate_in_mandelbrot_set(
        real: float,
        imaginary: float,
    ) -> bool:
        """
        Estimates whether or not the point of (`real`, `imaginary`) is inside the
        Mandelbrot set's cardioid or a second-order bulb.

        `True` indicates certainty that the point is within the cardioid or a
        second-order bulb. `False` indicates uncertainty whether the point is inside
        or outside.
        """

        # Check cardioid:

        imaginary_squared = imaginary * imaginary

        real_minus_quarter = real - 0.25

        q = (real_minus_quarter * real_minus_quarter) + imaginary_squared

        if q * (q + real_minus_quarter) <= (0.25 * imaginary_squared):
            return True

        # Check bulbs:

        real_plus_one = real + 1

        return (real_plus_one * real_plus_one) + imaginary_squared <= 0.0625

    @staticmethod
    def iterations_to_color_rows(
        height: int,
        working_directory: str,
    ) -> Iterator[list[int]]:
        colors: list[int] = []

        for y in range(height):
            if y > 0:
                yield colors
                colors = []

            path = join(working_directory, str(y))

            with open(path, "rb") as f:
                while r_bytes := f.read(16):
                    r = int.from_bytes(r_bytes)
                    g = int.from_bytes(f.read(16))
                    b = int.from_bytes(f.read(16))

                    colors.extend([r, g, b])

        yield colors
