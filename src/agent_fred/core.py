from typing import Any

from eparse.core import df_serialize_table, get_df_from_file
from eparse.interfaces import ExcelParse, i_factory
from haystack import Document


def load_prompt(filename: str) -> str:
    """load and return prompt template"""
    with open(filename, "r") as f:
        return f.read()


def xlsx_to_serialized_list(filename: str) -> list[dict[str, Any]]:
    """parse excel spreadsheet and return serialized list of cells"""
    result = []
    for (
        table, excel_rc, name, sheet,
    ) in get_df_from_file(filename, loose=False):
        for row in df_serialize_table(
            table, name=name, sheet=sheet, f_name=filename,
        ):
            result.append(row)

    return result


def xlsx_to_haystack_docs(filename: str) -> list[Document]:
    """parse excel spreadsheet and return list of haystack documents"""
    result = []
    for row in xlsx_to_serialized_list(filename):
        content = f"{row['c_header']} and {row['r_header']} is {row['value']}"
        result.append(Document(content=content))

    return result


def xlsx_to_db(filename: str) -> None:
    """parse excel spreadsheet into in-memory sqlite database"""
    db = i_factory("sqlite3:///:memory:", ExcelParse)
    for (
        table, excel_rc, name, sheet,
    ) in get_df_from_file(filename, loose=False):
        db.output(
            df_serialize_table(
                table, name=name, sheet=sheet, f_name=filename,
            ),
        )
