from pathlib import Path

#loads the request library
import requests
import pandas as pd

from src.validation.validators import validate_dublin_bikes
from src.database.postgres import load_dataframe_to_postgres


#stores the data-source address in a variable
URL = "https://data.smartdublin.ie/dublinbikes-api/bikes/dublin_bikes/current/stations.geojson"

#send an HTTP GET request to this URL and wait no longer than 30 seconds
#API call- python script contacted the dublin bikes endpoint and asked for the current data
response = requests.get(URL, timeout=30)

#if the server returns an error, this will raise an exception rather than letting the pipeline continue with bad data
response.raise_for_status()

#convert the JSON to python data/objects
data = response.json()
features = data["features"]

#list to hold station records cos the geojson feature is nested. we want to convert each station into one flat python dictionary
#all the station records will go into stations list
stations = []

#loop through every station
#for every station in the API response, get its properties and geographic coordinates
for feature in features:
    properties = feature["properties"]
    coordinates = feature["geometry"]["coordinates"]

    station = {
        "station_id": properties["station_id"],
        "name": properties["name"],
        "address": properties["address"],
        "latitude": coordinates[1],
        "longitude": coordinates[0],
        "capacity": properties["capacity"],
        "num_bikes_available": properties["num_bikes_available"],
        "num_docks_available": properties["num_docks_available"],
        "is_installed": properties["is_installed"],
        "is_renting": properties["is_renting"],
        "is_returning": properties["is_returning"],
        "last_reported_dt": properties["last_reported_dt"],
    }

    stations.append(station)

df = pd.DataFrame(stations)
df["ingested_at"] = pd.Timestamp.now(tz="UTC")

#save raw snapshot
raw_dir = Path("data/raw")
raw_dir.mkdir(parents=True, exist_ok=True)
timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y%m%d_%H%M%S")

raw_file = raw_dir / f"dublin_bikes_{timestamp}.csv"

df.to_csv(raw_file, index=False)

#validate data
valid_df, invalid_df = validate_dublin_bikes(df)

print(f"Records received: {len(df)}")
print(f"Valid records: {len(valid_df)}")
print(f"Invalid records: {len(invalid_df)}")

#quarantine bad records
if not invalid_df.empty:
    quarantine_dir = Path("data/quarantine")
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    quarantine_file = (
        quarantine_dir
        / f"dublin_bikes_invalid_{timestamp}.csv"
    )

    invalid_df.to_csv(
        quarantine_file,
        index=False,
    )

    print(
        f"Invalid records saved to: {quarantine_file}"
    )

print(f"Raw snapshot saved to: {raw_file}")

#convert timestamp column to a proper datetime type
valid_df["last_reported_dt"] = pd.to_datetime(
    valid_df["last_reported_dt"],
    errors="raise",
)

#load valid records into postgresql
if not valid_df.empty:
    load_dataframe_to_postgres(
        valid_df,
        table_name="dublin_bikes_station_status",
        schema="raw",
    )


output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y%m%d_%H%M%S")

output_file = output_dir / f"dublin_bikes_{timestamp}.csv"

df.to_csv(output_file, index=False)

print("Rows and columns:", df.shape)
print(df.head())




