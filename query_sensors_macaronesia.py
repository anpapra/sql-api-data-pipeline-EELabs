# This script retrieves the active devices (emitting in the last 5 days) within the Macaronesia
# It also retrieves the device's ID where available.
# The output CSV contains 'name' 'sensor_id', 'id', 'region' and 'place'.

import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from influxdb import InfluxDBClient

### Load environment variables --------
load_dotenv()
host = os.getenv("host")
port = int(os.getenv("port"))
username = os.getenv("username")
password = os.getenv("password")
database = os.getenv("database")

### Constants ----------
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_FILE = OUTPUT_DIR / "active_devices_macaronesia.csv"

### InfluxDB Client -----------
client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)

t1 = datetime.utcnow()
t2 = t1 - timedelta(hours=120)  # last 5 days

t1_str = t1.strftime('%Y-%m-%dT%H:%M:%SZ')
t2_str = t2.strftime('%Y-%m-%dT%H:%M:%SZ')

### Device metadata ------
device_info = {
    "DEVICE1": {"Region": "Archipelago1", "Place": "Place1"},
    "DEVICE2": {"Region": "Archipelago1", "Place": "Place2"},
    "DEVICE3": {"Region": "Archipelago2", "Place": "Place3"},
    "DEVICE4": {"Region": "Archipelago3", "Place": "Place4"},
    "DEVICE5": {"Region": "Archipelago1", "Place": "Place5"},
    "DEVICE7": {"Region": "Archipelago1", "Place": "Place7"},
}

### Get all points in the time range --------
query1 = f"""
SELECT * FROM sensor_measurement
WHERE time > '{t2_str}' AND time <= '{t1_str}'
"""
result1 = client.query(query1)
df1 = pd.DataFrame(list(result1.get_points()))

if not df1.empty:
    # Parse timestamps safely
    df1['time'] = pd.to_datetime(df1['time'], format='mixed', utc=True)

    # Get unique names
    unique_names = df1['name'].drop_duplicates().tolist()
    print(f"Found {len(unique_names)} unique names")

    device_records = []

    # Retrieve sensor_id and id for each device
    for name in unique_names:
        # Get sensor_id
        query_uid = f"""
        SELECT "sensor_id" FROM sensor_measurement
        WHERE "name" = '{name}' 
        LIMIT 1
        """
        res_uid = client.query(query_uid)
        points_uid = list(res_uid.get_points())
        sensor_id = points_uid[0]['sensor_id'] if points_uid and points_uid[0].get('sensor_id') else "MISSING"

        # Get id tag
        query_id = f"""
        SELECT "id" FROM sensor_measurement
        WHERE "name" = '{name}'
        LIMIT 1
        """
        res_id = client.query(query_id)
        points_id = list(res_id.get_points())
        device_id = points_id[0]['id'] if points_id and points_id[0].get('id') else "MISSING"

        # Check device_info prefix
        prefix = next((p for p in device_info.keys() if name.startswith(f"{p}_")), None)
        if prefix is None:
            continue  # skip unknown devices

        # Append combined record
        device_records.append({
            "name": name,
            "sensor_id": sensor_id,
            "id": device_id,
            "Region": device_info[prefix]['Region'],
            "Place": device_info[prefix]['Place'],
        })

    # --- Save CSV ---
    df_to_save = pd.DataFrame(device_records).drop_duplicates()
    df_to_save.to_csv(CSV_FILE, index=False)
    print(f"Saved {len(df_to_save)} matched devices with unique_id, id, and metadata to {CSV_FILE}")

else:
    print("No data found in this time range.")
