from pathlib import Path

import pandas as pd
import requests

from src.validation.validators import validate_weather_data
from src.database.postgres import load_dataframe_to_postgres



COLLECTION_ID = "observations-swob-nrt-60min"
LOCATION_ID = "3"

STATION_NAME = "Phoenix Park"
COUNTY = "Dublin"

WEATHER_PARAMETERS = [
    "air_temperature",
    "precipitation_amount",
    "relative_humidity",
    "air_pressure",
    "wind_speed",
    "wind_direction",
]


def fetch_weather_data():
    """Fetch hourly weather observations for Phoenix Park."""

    url = (
        f"https://opendata2.met.ie/edr/collections/"
        f"{COLLECTION_ID}/locations/{LOCATION_ID}"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


def create_weather_dataframe(data):
    """Transform Met Éireann observations into an analytics-friendly DataFrame."""

    items = data.get("items", [])

    df = pd.DataFrame(items)

    # Keep only the weather measurements needed for this project.
    df = df[df["parameter_name"].isin(WEATHER_PARAMETERS)].copy()

    # Convert the observation timestamp to a real datetime.
    df["observed_at"] = pd.to_datetime(
        df["observed_at"],
        utc=True,
    )

    # Convert the API's long-format measurements into
    # one row per weather observation time.
    weather_df = (
        df.pivot_table(
            index="observed_at",
            columns="parameter_name",
            values="value_num",
            aggfunc="first",
        )
        .reset_index()
    )

    weather_df.columns.name = None

    # Add information identifying the weather station.
    weather_df.insert(0, "station_id", int(LOCATION_ID))
    weather_df.insert(1, "station_name", STATION_NAME)
    weather_df.insert(2, "county", COUNTY)

    # Record when our pipeline collected the data.
    weather_df["ingested_at"] = pd.Timestamp.now(tz="UTC")

    return weather_df

def save_raw_snapshot(weather_df):
    """Save a timestamped copy of the weather data."""

    output_directory = Path("data/raw/weather")
    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y%m%d_%H%M%S")

    output_path = (
        output_directory
        / f"phoenix_park_weather_{timestamp}.csv"
    )

    weather_df.to_csv(output_path, index=False)

    print(f"Raw weather snapshot saved to: {output_path}")

def save_invalid_weather_records(invalid_df):
    """Save invalid weather observations for investigation."""

    if invalid_df.empty:
        print("No invalid weather records to quarantine.")
        return

    output_directory = Path("data/quarantine/weather")
    output_directory.mkdir(parents=True, exist_ok=True)

    timestamp = pd.Timestamp.now(tz="UTC").strftime("%Y%m%d_%H%M%S")

    output_path = (
        output_directory
        / f"phoenix_park_weather_invalid_{timestamp}.csv"
    )

    invalid_df.to_csv(output_path, index=False)

    print(f"Invalid weather records saved to: {output_path}")


def main():
    data = fetch_weather_data()

    weather_df = create_weather_dataframe(data)

    save_raw_snapshot(weather_df)

    #temporrily test with one invalid humidity value
    #weather_df.loc[weather_df.index[0], "relative_humidity"] = 150

    valid_df, invalid_df = validate_weather_data(weather_df)

    print(f"Weather records received: {len(weather_df)}")
    print(f"Valid weather records: {len(valid_df)}")
    print(f"Invalid weather records: {len(invalid_df)}")   

    save_invalid_weather_records(invalid_df)

    load_dataframe_to_postgres(
        valid_df,
        table_name="phoenix_park_weather",
        schema="raw",
    )


    print("Weather data retrieved successfully.")
    print("Station:", STATION_NAME)
    print("Rows and columns:", weather_df.shape)

    print("\nColumns:")
    print(weather_df.columns.tolist())

    print("\nLatest 5 weather observations:")
    print(
        weather_df.sort_values("observed_at")
        .tail(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()