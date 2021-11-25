from os import path

from django.test import SimpleTestCase

from .csv import CsvService

TESTDATA_FOLDER = path.join(path.dirname(__file__), "test")


class TestCsvParse(SimpleTestCase):
    """
    Parsing string or byte IO object to internal representation.
    """

    def setUp(self):
        self.service = CsvService()
        self.schema = {"one": "egy", "three": "harom"}

    def test_normal_csv_with_comma(self):
        with open(path.join(TESTDATA_FOLDER, "normal_with_commas.csv")) as f:
            result = self.service.parse(f, self.schema)
            self.assertSequenceEqual(
                tuple(result),
                ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
            )

    def test_normal_csv_with_semicolon(self):
        with open(path.join(TESTDATA_FOLDER, "normal_with_semicolons.csv")) as f:
            result = self.service.parse(f, self.schema)
            self.assertSequenceEqual(
                tuple(result),
                ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
            )

    def test_missing_delimiter_from_header(self):
        with open(path.join(TESTDATA_FOLDER, "missing_delimiter.csv")) as f:
            with self.assertRaises(ValueError) as manager:
                self.service.parse(f, self.schema)
            self.assertEqual(
                str(manager.exception),
                "Couldn't guess separator, because no possible delimiters are present in the header.",
            )

    def test_ambigous_delimiter_from_header(self):
        with open(path.join(TESTDATA_FOLDER, "ambigous_delimiter.csv")) as f:
            with self.assertRaises(ValueError) as manager:
                self.service.parse(f, self.schema)
            self.assertEqual(
                str(manager.exception),
                "Couldn't guess separator, because both , ; are possible candidates.",
            )

    def test_unknown_item_in_schema(self):
        with open(path.join(TESTDATA_FOLDER, "normal_with_commas.csv")) as f:
            with self.assertRaises(ValueError) as manager:
                self.service.parse(f, {**self.schema, "Hello": "hello"})
            self.assertEqual(
                str(manager.exception),
                "Couldn't find Hello in the header, so we are unable to map it properly.",
            )

    def test_normal_csv_in_binary_format(self):
        with open(path.join(TESTDATA_FOLDER, "normal_with_commas.csv"), "rb") as f:
            result = self.service.parse(f, self.schema)
            self.assertSequenceEqual(
                tuple(result),
                ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
            )

    def test_csv_with_empty_last_row(self):
        with open(path.join(TESTDATA_FOLDER, "empty_last_row.csv")) as f:
            result = self.service.parse(f, self.schema)
            self.assertSequenceEqual(
                tuple(result),
                ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
            )

    def test_csv_with_empty_first_row(self):
        with open(path.join(TESTDATA_FOLDER, "empty_first_row.csv")) as f:
            result = self.service.parse(f, self.schema)
            self.assertSequenceEqual(
                tuple(result),
                ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
            )

    def test_csv_with_empty_intermediate_row(self):
        with open(path.join(TESTDATA_FOLDER, "empty_intermediate_row.csv")) as f:
            result = self.service.parse(f, self.schema)
            self.assertSequenceEqual(
                tuple(result),
                ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
            )

    def test_csv_with_less_cells_in_a_line(self):
        with open(path.join(TESTDATA_FOLDER, "missing_cell.csv")) as f:
            with self.assertRaises(Exception) as manager:
                self.service.parse(f, self.schema)
            self.assertEqual(
                str(manager.exception),
                "Malformed CSV file.",
            )


class TestCsvFromFile(SimpleTestCase):
    """
    Opening a file object and parsing it to internal representation.
    """

    def setUp(self):
        self.service = CsvService()
        self.schema = {"one": "egy", "three": "harom"}

    def test_normal_csv_file(self):
        result = self.service.from_file(
            path.join(TESTDATA_FOLDER, "normal_with_commas.csv"), self.schema
        )
        self.assertSequenceEqual(
            tuple(result),
            ({"egy": "1", "harom": "3"}, {"egy": "hola", "harom": "hello"}),
        )

    def test_exception_passthrough(self):
        with self.assertRaises(ValueError) as manager:
            self.service.from_file(
                path.join(TESTDATA_FOLDER, "ambigous_delimiter.csv"), self.schema
            )
        self.assertEqual(
            str(manager.exception),
            "Couldn't guess separator, because both , ; are possible candidates.",
        )
