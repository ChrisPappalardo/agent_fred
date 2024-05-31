import datetime as dt
import pandas as pd
import sys
import uuid
from io import StringIO

from agent_fred.core import get_fred_data_series


if __name__ == "__main__":
    print("get fred data from api")

    while True:
        try:
            series_id = input("series_id [GDPC1]? ") or "GDPC1"
            now = dt.datetime.now().strftime("%Y-%m-%d")
            start_date = input(f"start date [{now}]? ") or now
            end_date = input(f"end date [{now}]? ") or now

            fred_df = get_fred_data_series(
                series_id=series_id,
                start_date=start_date,
                end_date=end_date,
            )

            if input("save as xlsx [n]? "):
                filename = f"{uuid.uuid4()}.xlsx"
                filename = input(f"filename [{filename}]: ") or filename
                pd.read_json(StringIO(fred_df)).to_excel(filename)

            else:
                print(fred_df)

        except KeyboardInterrupt:
            print("exiting...")
            sys.exit(0)
