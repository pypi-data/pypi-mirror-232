import csv
import itertools
from typing import TextIO

from .renderers import BaseRenderer, JSONRenderer


class CSVConverter:
    @classmethod
    def convert(
        cls,
        f: TextIO,
        output_format: str,
        skip_rows: int | None = None,
        take_rows: int | None = None,
    ) -> str:
        if skip_rows is not None and take_rows is not None:
            take_rows = skip_rows + take_rows

        rows = [
            row for row in itertools.islice(csv.DictReader(f), skip_rows, take_rows)
        ]

        renderer = cls._get_renderer(output_format)
        rendered_rows = renderer.render(rows)

        return rendered_rows

    @staticmethod
    def _get_renderer(output_format: str) -> BaseRenderer:
        match output_format:
            case "json":
                return JSONRenderer()
            case _:
                raise ValueError(f'The "{output_format}" format is not supported.')


csv_converter = CSVConverter()
