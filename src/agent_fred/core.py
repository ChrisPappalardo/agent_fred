from eparse.core import df_serialize_table, get_df_from_file
from haystack import Document


def xlsx_to_haystack_docs(filename: str) -> list[Document]:
    result = []
    for (
        table, excel_rc, name, sheet,
    ) in get_df_from_file(filename, loose=False):
        for row in df_serialize_table(
            table, name=name, sheet=sheet, f_name=filename,
        ):
            content = f"{row['c_header']} and {row['r_header']} is {row['value']}"
            result.append(Document(content=content))

    return result
