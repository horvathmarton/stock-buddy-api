"""
CSV handling related service.
"""

from functools import reduce
from typing import Callable, Dict, Generator, List, TextIO, Tuple

ParsedRow = Dict[str, str]


class CsvService:
    """
    This service could parse a CSV file based on file path or buffer.
    """

    def from_file(
        self, path: str, schema: Dict[str, str]
    ) -> Generator[ParsedRow, None, None]:
        """
        Reads the file at the given path and parses it to a tuple of dicts based on the provided schema.
        """

        with open(path, encoding="utf-8") as file:
            return self.parse(file, schema)

    def parse(
        self, buffer: TextIO, schema: Dict[str, str]
    ) -> Generator[ParsedRow, None, None]:
        """
        Parses the passed buffer to a tuple of dicts based on the provided schema.
        """

        try:
            content = buffer.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            # We remove empty lines with the conditional.
            lines = [line for line in content.split("\n") if line]

            header = lines[0]
            delimiter = self.__guess_delimiter(header)
            header_index = self.__index_header(header, delimiter, schema)

            # We remove the first row as we don't want to parse the header.
            cells_count = len(header.split(delimiter))
            data_lines = []
            for line in lines[1:]:
                cells = line.split(delimiter)
                if len(cells) != cells_count:
                    raise Exception(
                        "Cells count is not equal to cells count in the header."
                    )

                data_lines.append(cells)

            return (
                {name: cells[idx] for name, idx in header_index.items()}
                for cells in data_lines
            )
        except ValueError:
            raise
        except Exception as exception:
            raise Exception("Malformed CSV file.") from exception

    @staticmethod
    def __guess_delimiter(header: str) -> str:
        """
        Tries to find out the delimiter of the file based on the header.

        Raises ValueError if unsuccessful.
        """

        possible_delimiters = (",", ";", "\t", "|")
        delimiter_candidates = [
            delimiter for delimiter in possible_delimiters if delimiter in header
        ]

        if len(delimiter_candidates) == 0:
            raise ValueError(
                "Couldn't guess separator, because no possible delimiters are present in the header."
            )

        if len(delimiter_candidates) != 1:
            raise ValueError(
                f"Couldn't guess separator, because both {' '.join(delimiter_candidates)} are possible candidates."
            )

        return delimiter_candidates[0]

    def __index_header(
        self, header: str, delimiter: str, schema: Dict[str, str]
    ) -> Dict[str, int]:
        """
        Generates and index where the key is the alias for the column and the value is the index in a CSV row.
        """

        header_cells = header.split(delimiter)

        return reduce(
            self.__create_header_index_finder(header_cells), schema.items(), {}
        )

    @staticmethod
    def __create_header_index_finder(
        header_cells: List[str],
    ) -> Callable[[Dict[str, int], Tuple[str, str]], Dict[str, int]]:
        """
        Factory method to find a named cell's position from the list or raise custom ValueError.
        """

        def find_header_index(
            index: Dict[str, int], header_mapping: Tuple[str, str]
        ) -> Dict[str, int]:
            name, alias = header_mapping
            try:
                idx = header_cells.index(name)
                index[alias] = idx

                return index
            except ValueError as error:
                raise ValueError(
                    f"Couldn't find {name} in the header, so we are unable to map it properly."
                ) from error

        return find_header_index