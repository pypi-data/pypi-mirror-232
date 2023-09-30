import json
from io import StringIO

import pytest

from converter.core import csv_converter


@pytest.fixture
def input_data():
    return StringIO(
        "User,Workstation Type,Serial Number,CPU,RAM,SSD\n"
        "Tom White,Laptop,2889900,AMD Ryzen 7,64GB,10TB\n"
        "John Doe,Laptop,112233,Intel i7,32GB,2TB\n"
        "Barbara Black,PC,556677,Intel i5,16GB,1TB\n"
        "Steve Jones,PC,121212,Intel i3,8GB,512GB"
    )


@pytest.mark.parametrize(
    "skip_rows, take_rows, expected_result",
    [
        (
            None,
            None,
            """
                [
                    {
                        "User": "Tom White",
                        "Workstation Type": "Laptop",
                        "Serial Number": "2889900",
                        "CPU": "AMD Ryzen 7",
                        "RAM": "64GB",
                        "SSD": "10TB"
                    },
                    {
                        "User": "John Doe",
                        "Workstation Type": "Laptop",
                        "Serial Number": "112233",
                        "CPU": "Intel i7",
                        "RAM": "32GB",
                        "SSD": "2TB"
                    },
                    {
                        "User": "Barbara Black",
                        "Workstation Type": "PC",
                        "Serial Number": "556677",
                        "CPU": "Intel i5",
                        "RAM": "16GB",
                        "SSD": "1TB"
                    },
                    {
                        "User": "Steve Jones",
                        "Workstation Type": "PC",
                        "Serial Number": "121212",
                        "CPU": "Intel i3",
                        "RAM": "8GB",
                        "SSD": "512GB"
                    }
                ]
                """,
        ),
        (
            1,
            None,
            """
                [
                    {
                        "User": "John Doe",
                        "Workstation Type": "Laptop",
                        "Serial Number": "112233",
                        "CPU": "Intel i7",
                        "RAM": "32GB",
                        "SSD": "2TB"
                    },
                    {
                        "User": "Barbara Black",
                        "Workstation Type": "PC",
                        "Serial Number": "556677",
                        "CPU": "Intel i5",
                        "RAM": "16GB",
                        "SSD": "1TB"
                    },
                    {
                        "User": "Steve Jones",
                        "Workstation Type": "PC",
                        "Serial Number": "121212",
                        "CPU": "Intel i3",
                        "RAM": "8GB",
                        "SSD": "512GB"
                    }
                ]
                """,
        ),
        (
            2,
            2,
            """
                [
                    {
                        "User": "Barbara Black",
                        "Workstation Type": "PC",
                        "Serial Number": "556677",
                        "CPU": "Intel i5",
                        "RAM": "16GB",
                        "SSD": "1TB"
                    },
                    {
                        "User": "Steve Jones",
                        "Workstation Type": "PC",
                        "Serial Number": "121212",
                        "CPU": "Intel i3",
                        "RAM": "8GB",
                        "SSD": "512GB"
                    }
                ]
                """,
        ),
        (
            2,
            1,
            """
                [
                    {
                        "User": "Barbara Black",
                        "Workstation Type": "PC",
                        "Serial Number": "556677",
                        "CPU": "Intel i5",
                        "RAM": "16GB",
                        "SSD": "1TB"
                    }
                ]
                """,
        ),
    ],
)
def test_converter_with_json_format(input_data, skip_rows, take_rows, expected_result):
    result = csv_converter.convert(
        input_data, output_format="json", skip_rows=skip_rows, take_rows=take_rows
    )
    assert json.loads(result) == json.loads(expected_result)
