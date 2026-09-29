from pathlib import Path

import pandas as pd
import requests

from src.database.postgres import load_dataframe_to_postgres
from src.validation.validators import validate_dublin_bikes


URL = "https://data.smartdublin.ie/dublinbikes-api/bikes/dublin_bikes/current/stations.geojson"


def fetch_dublin_bikes():
    """Fetch the current Dublin Bikes station feed."""
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    return response.json()


def create_station_dataframe(data):
    """Flatten the GeoJSON station features into a dataframe."""
    stations = []

    for feature in data["features"]:
        properties = feature["properties"]
        coordinates = feature["geometry"]["coordinates"]

        stations.append(
            {
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
        )

    df = pd.DataFrame(stations)
    df["ingested_at"] = pd.Timestamp.now(tz="UTC")

    return df


def save_raw_snapshot(df, timestamp):
    """Save the unmodified API snapshot before validation."""
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_file = raw_dir / f"dublin_bikes_{timestamp}.csv"
    df.to_csv(raw_file, index=False)

    return raw_file


def save_invalid_records(invalid_df, timestamp):
    """Quarantine records that fail validation."""
    if invalid_df.empty:
        return None

    quarantine_dir = Path("data/quarantine")
    quarantine_dir.mkdir(parents=True, exist_ok=True)

    quarantine_file = (
        quarantine_dir / f"dublin_bikes_invalid_{timestamp}.csv"
    )

    invalid_df.to_csv(quarantine_file, index=False)

    return quarantine_file


def main():
    data = fetch_dublin_bikes()
    df = create_station_dataframe(data)

    timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y%m%d_%H%M%S")
    raw_file = save_raw_snapshot(df, timestamp)

    valid_df, invalid_df = validate_dublin_bikes(df)

    print(f"Records received: {len(df)}")
    print(f"Valid records: {len(valid_df)}")
    print(f"Invalid records: {len(invalid_df)}")
    print(f"Raw snapshot saved to: {raw_file}")

    quarantine_file = save_invalid_records(invalid_df, timestamp)

    if quarantine_file is not None:
        print(f"Invalid records saved to: {quarantine_file}")

    valid_df = valid_df.copy()

    valid_df["last_reported_dt"] = pd.to_datetime(
        valid_df["last_reported_dt"],
        errors="raise",
    )

    if not valid_df.empty:
        load_dataframe_to_postgres(
            valid_df,
            table_name="dublin_bikes_station_status",
            schema="raw",
        )

    print("Rows and columns:", df.shape)
    print(df.head())


if __name__ == "__main__":
    main()