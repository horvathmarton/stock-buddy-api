from functools import reduce
from typing import Callable, Dict, ItemsView, List, TextIO

ParsedRow = Dict[str, str]

# TODO: Rework me to use the built-in csv module.
class CsvService:
    """
    This service could parse a CSV file based on file path or buffer.
    """

    def is_csv_file(self, file: TextIO) -> bool:
        """
        Tries to detect if the file is a valid CSV file or not.
        """

        raise NotImplementedError('Implement is_csv_file')

    def from_file(self, path: str, schema: Dict[str, str]) -> List[ParsedRow]:
        """
        Reads the file at the given path and parses it to a tuple of dicts based on the provided schema.
        """

        with open(path) as f:
            return self.parse(f, schema)

    def parse(self, buffer: TextIO, schema: Dict[str, str]) -> List[ParsedRow]:
        """
        Parses the passed buffer to a tuple of dicts based on the provided schema.
        """

        content = buffer.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        content = content.split('\n')

        header = content[0]
        delimiter = self.__guess_delimiter(header)
        header_index = self.__index_header(header, delimiter, schema)

        # We remove the first row as we don't want to parse the header.
        # We also remove empty lines with the conditional.
        lines = (line.split(delimiter) for line in content[1:] if line)

        # TODO: What happens if one of the lines has less cells?
        # TODO: What happens with a CSV with an empty last line?
        return (
            {name: cells[idx] for name, idx in header_index.items()}
            for cells in lines
        )

    def __guess_delimiter(self, header: str) -> chr:
        """
        Tries to find out the delimiter of the file based on the header.

        Raises ValueError if unsuccessful.
        """

        possible_delimiters = (',', ';', '\t', '|')
        delimiter_candidates = [
            delimiter for delimiter in possible_delimiters if delimiter in header]

        if len(delimiter_candidates) == 0:
            raise ValueError(
                f"Couldn't guess separator, because no possible delimiters are present in the header.")
        elif len(delimiter_candidates) != 1:
            raise ValueError(
                f"Couldn't guess separator, because both {' '.join(delimiter_candidates)} are possible candidates.")

        return delimiter_candidates[0]

    def __index_header(self, header: str, delimiter: chr, schema: Dict[str, str]) -> Dict[str, int]:
        """
        Generates and index where the key is the alias for the column and the value is the index in a CSV row.
        """

        header_cells = header.split(delimiter)

        return reduce(self.__create_header_index_finder(header_cells), schema.items(), {})

    def __create_header_index_finder(self, header_cells: List[str]) -> Callable[[int, List[ItemsView[str, str]]], int]:
        """
        Factory method to find a named cell's position from the list or raise custom ValueError.
        """

        def find_header_index(index: int, header_mapping: List[ItemsView[str, str]]) -> int:
            name, alias = header_mapping
            try:
                idx = header_cells.index(name)
                index[alias] = idx

                return index
            except ValueError:
                raise ValueError(
                    f"Couldn't find {name} in the header, so we are unable to map it properly.")

        return find_header_index
