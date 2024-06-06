"""main method to extract fred data series using based opn user input and write to Excel file"""

import pandas as pd

from agent_fred.config import config
from agent_fred.core import get_fred_data_series

if __name__ == "__main__":
    print(
        "method for extracting fred data series defined by the user input of a value (series_id),"
        " along with corresponding start and end dates  and writing the result to an excel file."
    )
    # get desired observation series_id from user
    default_series_id = "GDPC1"
    user_defined_series = input(
        "What is the series you would like agent fred to extract?"
    )
    series_id = input(f"load [{user_defined_series}]: ") or default_series_id
    default_start_date = "2023-01-01"
    default_end_date = "2024-01-01"
    user_defined_start_date = input(
        "What would you like the start date to be. Please input in the format YYYY-MM-DD: "
    )
    start_date = input(f"load [{user_defined_start_date}]: ") or default_start_date
    user_defined_end_date = input(
        "What would you like the end date to be. Please input in the format YYYY-MM-DD: "
    )
    end_date = input(f"load [{user_defined_end_date}]: ") or default_end_date
    fred_df = get_fred_data_series(
        api_key=config.api_key,
        series_id=series_id,
        file_type="json",
        start_date=start_date,
        end_date=end_date,
    )
    # extract relevant value from "observations" dictionary in dataframe
    fred_df["GDP_Billions"] = [x["value"] for x in fred_df["observations"].values[:]]
    base_path = "src/agent_fred/api_data/"
    output_file_name = "fred_data_series.xlsx"
    with pd.ExcelWriter(base_path + output_file_name) as writer:
        fred_df.to_excel(writer, sheet_name=series_id)
    print(f"Saved fred data series to {base_path}{output_file_name}.")
