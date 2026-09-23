from pathlib import Path

import pandas as pd

from src.database.postgres import load_dataframe_to_postgres

GTFS_DIRECTORY = Path("data/raw/gtfs")


def load_gtfs_routes():
    """Read the NTA static GTFS routes file."""

    file_path = GTFS_DIRECTORY / "routes.txt"

    routes_df = pd.read_csv(
        file_path,
        dtype=str,
    )

    print(f"GTFS routes received: {len(routes_df)}")
    print(f"Routes rows and columns: {routes_df.shape}")

    return routes_df


def load_gtfs_trips():
    """Read the NTA static GTFS trips file."""

    file_path = GTFS_DIRECTORY / "trips.txt"

    trips_df = pd.read_csv(
        file_path,
        dtype=str,
    )

    print(f"GTFS trips received: {len(trips_df)}")
    print(f"Trips rows and columns: {trips_df.shape}")

    load_dataframe_to_postgres(
        trips_df,
        table_name="gtfs_trips",
        schema="raw",
    )

    return trips_df


def load_gtfs_stops():
    """Read the NTA static GTFS stops file."""

    file_path = GTFS_DIRECTORY / "stops.txt"

    stops_df = pd.read_csv(
        file_path,
        dtype=str,
    )

    print(f"GTFS stops received: {len(stops_df)}")
    print(f"Stops rows and columns: {stops_df.shape}")

    # Convert coordinate columns to numbers.
    stops_df["stop_lat"] = pd.to_numeric(
        stops_df["stop_lat"],
        errors="coerce",
    )

    stops_df["stop_lon"] = pd.to_numeric(
        stops_df["stop_lon"],
        errors="coerce",
    )

    # Convert location_type to integer when present.
    stops_df["location_type"] = pd.to_numeric(
        stops_df["location_type"],
        errors="coerce",
    ).astype("Int64")

    # Convert missing pandas values to Python None
    # so PostgreSQL stores them as NULL.
    stops_df = stops_df.astype(object).where(
        stops_df.notna(),
        None,
    )

    load_dataframe_to_postgres(
        stops_df,
        table_name="gtfs_stops",
        schema="raw",
    )

    return stops_df

def load_gtfs_stop_times():
    """Read and load the NTA static GTFS stop times file in chunks."""

    file_path = GTFS_DIRECTORY / "stop_times.txt"

    chunk_size = 50000
    total_records = 0

    stop_times_chunks = pd.read_csv(
        file_path,
        dtype=str,
        chunksize=chunk_size,
    )

    for chunk_number, stop_times_df in enumerate(
        stop_times_chunks,
        start=1,
    ):
        # stop_sequence is stored as an integer in PostgreSQL.
        stop_times_df["stop_sequence"] = pd.to_numeric(
            stop_times_df["stop_sequence"],
            errors="coerce",
        ).astype("Int64")

        # Convert pandas missing values to Python None
        # so PostgreSQL stores them as NULL.
        stop_times_df = stop_times_df.astype(object).where(
            stop_times_df.notna(),
            None,
        )

        load_dataframe_to_postgres(
            stop_times_df,
            table_name="gtfs_stop_times",
            schema="raw",
        )

        total_records += len(stop_times_df)

        print(
            f"Processed stop-times chunk {chunk_number}: "
            f"{total_records} records so far"
        )

    print(
        f"GTFS stop times received: {total_records}"
    )

    return total_records


def main():
    """Run the static GTFS ingestion pipeline."""

    routes_df = load_gtfs_routes()
    trips_df = load_gtfs_trips()
    stops_df = load_gtfs_stops()
    stop_times_count = load_gtfs_stop_times()

    print()
    print("Static GTFS ingestion completed successfully.")
    print()
    print(f"Routes: {len(routes_df)}")
    print(f"Trips: {len(trips_df)}")
    print(f"Stops: {len(stops_df)}")
    print(f"Stop times: {stop_times_count}")


if __name__ == "__main__":
    main()