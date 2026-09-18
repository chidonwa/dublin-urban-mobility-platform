import os
from datetime import datetime, timezone

import pandas as pd
import requests
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2

from src.validation.validators import validate_nta_vehicles
from src.database.postgres import load_dataframe_to_postgres


load_dotenv()


NTA_VEHICLES_URL = "https://api.nationaltransport.ie/gtfsr/v2/Vehicles"


def fetch_vehicle_feed():
    """Request the latest GTFS-Realtime vehicle feed from the NTA."""

    api_key = os.getenv("NTA_API_KEY")

    if not api_key:
        raise ValueError("NTA_API_KEY was not found in the environment.")

    headers = {
        "x-api-key": api_key
    }

    response = requests.get(
        NTA_VEHICLES_URL,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    return feed


def transform_vehicle_feed(feed):
    """Transform GTFS-Realtime vehicle entities into a DataFrame."""

    records = []
    ingested_at = datetime.now(timezone.utc)

    for entity in feed.entity:
        vehicle = entity.vehicle

        record = {
            "entity_id": entity.id,
            "vehicle_id": vehicle.vehicle.id,
            "trip_id": vehicle.trip.trip_id,
            "route_id": vehicle.trip.route_id,
            "direction_id": vehicle.trip.direction_id,
            "start_time": vehicle.trip.start_time,
            "start_date": vehicle.trip.start_date,
            "latitude": vehicle.position.latitude,
            "longitude": vehicle.position.longitude,
            "observed_at": datetime.fromtimestamp(
                vehicle.timestamp,
                tz=timezone.utc,
            ),
            "ingested_at": ingested_at,
        }

        records.append(record)

    return pd.DataFrame(records)

def save_raw_snapshot(df):
    """Save a timestamped snapshot of the NTA vehicle data."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    file_path = (
        f"data/raw/nta/"
        f"nta_vehicles_{timestamp}.csv"
    )

    df.to_csv(file_path, index=False)

    print(f"Raw NTA snapshot saved to: {file_path}")

def save_invalid_records(invalid_df):
    """Save invalid NTA vehicle records to the quarantine directory."""

    if invalid_df.empty:
        print("No invalid NTA vehicle records to quarantine.")
        return

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    file_path = (
        f"data/quarantine/nta/"
        f"nta_vehicles_invalid_{timestamp}.csv"
    )

    invalid_df.to_csv(file_path, index=False)

    print(f"Invalid NTA records quarantined to: {file_path}")

def main():
    print("Requesting NTA vehicle data...")

    feed = fetch_vehicle_feed()

    print(f"Vehicle entities received: {len(feed.entity)}")

    df = transform_vehicle_feed(feed)

    print("NTA vehicle data transformed successfully.")
    print("Rows and columns:", df.shape)

    save_raw_snapshot(df)

    valid_df, invalid_df = validate_nta_vehicles(df)

    print("NTA vehicle records received:", len(df))
    print("Valid NTA vehicle records:", len(valid_df))
    print("Invalid NTA vehicle records:", len(invalid_df))

    save_invalid_records(invalid_df)

    load_dataframe_to_postgres(
        valid_df,
        table_name="nta_vehicle_positions",
        schema="raw",
    )

    print("\nFirst five records:")
    print(df.head())


if __name__ == "__main__":
    main()