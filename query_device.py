from datetime import datetime, timezone
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from influxdb import InfluxDBClient

### Load keys --------------
load_dotenv()

host = os.getenv("HOST")
port = int(os.getenv("PORT"))
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
database = os.getenv("DATABASE")

### File paths --------------
RAW_DATA_DIR = Path("raw-data")
RAW_DATA_DIR.mkdir(exist_ok=True)

CSV_FILE = RAW_DATA_DIR / "sg_group.csv"
TIMESTAMP_FILE = RAW_DATA_DIR / "last_query_SG.txt"

### Connect to InfluxDB ----------------
client = InfluxDBClient(
    host=host,
    port=port,
    username=username,
    password=password,
    database=database,
)

### Determine if an incremental query can be performed to avoid overloading the system ----------
use_incremental = False
last_query_time = None
current_time = datetime.now(timezone.utc)

if CSV_FILE.exists() and TIMESTAMP_FILE.exists():
    try:
        timestamp_str = TIMESTAMP_FILE.read_text().strip()

        if timestamp_str:
            last_query_time = pd.to_datetime(timestamp_str)

            if not pd.isna(last_query_time):
                use_incremental = True

    except Exception as e:
        print(
            f"Warning: Could not read timestamp file. "
            f"Running full query instead. ({e})"
        )

### Build query ---------
if use_incremental:

    print(
        f"Performing incremental query "
        f"since {last_query_time}..."
    )

    query = f"""
    SELECT *
    FROM sensor_measurements
    WHERE "name" =~ /^SENSOR.*$/
      AND time > '{last_query_time.isoformat()}'
    ORDER BY time ASC
    """

else:

    print("Performing full query for SENSOR photometers...")

    query = """
    SELECT *
    FROM sensor_measurements
    WHERE "name" =~ /^SENSOR.*$/
    ORDER BY time ASC
    """

### Execute query --------------
result = client.query(query)
data = list(result.get_points())

### Process and save data ------------
if data:

    df_new = pd.DataFrame(data)

    df_new["time"] = pd.to_datetime(
        df_new["time"],
        errors="coerce",
        utc=True,
    )

    df_new.dropna(subset=["time"], inplace=True)

    if use_incremental and CSV_FILE.exists():

        df_existing = pd.read_csv(
            CSV_FILE,
            parse_dates=["time"],
        )

        df_all = pd.concat(
            [df_existing, df_new],
            ignore_index=True,
        )

        df_all.drop_duplicates(
            subset=["time", "name"],
            inplace=True,
        )

        df_all.sort_values(
            by="time",
            inplace=True,
        )

    else:
        df_all = df_new

    df_all.to_csv(CSV_FILE, index=False)

    TIMESTAMP_FILE.write_text(
        current_time.isoformat()
    )

    print(
        f"Saved {len(df_all)} total number of records "
        f"to file {CSV_FILE}"
    )

else:
    print("No new data found.")
