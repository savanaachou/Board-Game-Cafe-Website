import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper import helper


def test_convert_true_false_become_one_and_zero():
    assert helper.convert("TRUE") == 1
    assert helper.convert("FALSE") == 0
    assert helper.convert("true") == 1
    assert helper.convert("false") == 0


def test_convert_empty_string_becomes_none():
    assert helper.convert("") is None


def test_convert_numeric_strings_become_numbers():
    assert helper.convert("42") == 42
    assert isinstance(helper.convert("42"), int)
    assert helper.convert("4.50") == 4.5
    assert isinstance(helper.convert("4.50"), float)


def test_convert_leaves_plain_text_as_string():
    assert helper.convert("Catan") == "Catan"


def test_data_cleaner_skips_header_row(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("name,price\nMatcha Latte,5.25\n")

    rows = helper.data_cleaner(str(csv_file))

    assert len(rows) == 1
    assert rows[0] == ("Matcha Latte", 5.25)


def test_data_cleaner_handles_quoted_commas(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        'name,description\n'
        '"Brown Sugar Milk Tea","Black milk tea, swirled with brown sugar syrup."\n'
    )

    rows = helper.data_cleaner(str(csv_file))

    assert rows[0] == ("Brown Sugar Milk Tea", "Black milk tea, swirled with brown sugar syrup.")


def test_data_cleaner_skips_blank_lines(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("name,price\nCatan,0\n\nChess,0\n")

    rows = helper.data_cleaner(str(csv_file))

    assert len(rows) == 2
