import pandas as pd

def validate_dublin_bikes(df: pd.DataFrame):
    """
    Validate Dublin Bikes station records.
    Returns:
        valid_df: records that passed validation
        invalid_df: records that failed one or more validation checks
    """
    validated_df = df.copy()

    #create an empty column that will contain validation errors
    validated_df["validation_error"] = ""

    required_columns = [
        "station_id",
        "name",
        "capacity",
        "num_bikes_available",
        "latitude",
        "longitude",
        "last_reported_dt",
    ]

    #check for missing required values
    for column in required_columns: 
        missing_mask = validated_df[column].isna()

        validated_df.loc[
            missing_mask, "validation_error"
        ] += f"missing_{column};"

    #check for blank station names
    blank_name_mask = (
        validated_df["name"]
        .astype(str)
        .str.strip()
        .eq("")
        )

    validated_df.loc[
        blank_name_mask, "validation_error"
        ] += "blank_station_name;"

    # Check for invalid capacity.
    invalid_capacity_mask = validated_df["capacity"] <= 0

    validated_df.loc[
        invalid_capacity_mask, "validation_error"
    ] += "invalid_capacity;"

    # Check for negative bike counts.
    negative_bikes_mask = (
        validated_df["num_bikes_available"] < 0
    )

    validated_df.loc[
        negative_bikes_mask, "validation_error"
    ] += "negative_bikes_available;"

    # Check for negative dock counts.
    negative_docks_mask = (
        validated_df["num_docks_available"] < 0
    )

    validated_df.loc[
        negative_docks_mask, "validation_error"
    ] += "negative_docks_available;"

    # Bikes should not exceed station capacity.
    bikes_over_capacity_mask = (
        validated_df["num_bikes_available"]
        > validated_df["capacity"]
    )

    validated_df.loc[
        bikes_over_capacity_mask, "validation_error"
    ] += "bikes_exceed_capacity;"

    # Docks should not exceed station capacity.
    docks_over_capacity_mask = (
        validated_df["num_docks_available"]
        > validated_df["capacity"]
    )

    validated_df.loc[
        docks_over_capacity_mask, "validation_error"
    ] += "docks_exceed_capacity;"

    # Latitude must be valid.
    invalid_latitude_mask = ~validated_df["latitude"].between(
        -90, 90
    )

    validated_df.loc[
        invalid_latitude_mask, "validation_error"
    ] += "invalid_latitude;"

    # Longitude must be valid.
    invalid_longitude_mask = ~validated_df["longitude"].between(
        -180, 180
    )

    validated_df.loc[
        invalid_longitude_mask, "validation_error"
    ] += "invalid_longitude;"

    # Check whether timestamps can be parsed correctly.
    parsed_timestamps = pd.to_datetime(
        validated_df["last_reported_dt"],
        errors="coerce",
    )

    invalid_timestamp_mask = parsed_timestamps.isna()

    validated_df.loc[
        invalid_timestamp_mask, "validation_error"
    ] += "invalid_last_reported_dt;"

    # Check for duplicate observations.
    duplicate_mask = validated_df.duplicated(
        subset=["station_id", "last_reported_dt"],
        keep=False,
    )

    validated_df.loc[
        duplicate_mask, "validation_error"
    ] += "duplicate_station_observation;"

    # Separate valid and invalid records.
    valid_df = validated_df[
        validated_df["validation_error"] == ""
    ].copy()

    invalid_df = validated_df[
        validated_df["validation_error"] != ""
    ].copy()

    # Remove validation_error from successful records.
    valid_df = valid_df.drop(columns=["validation_error"])

    return valid_df, invalid_df

def validate_weather_data(df):
    """Separate valid and invalid weather observations."""

    required_columns = [
        "station_id",
        "station_name",
        "observed_at",
        "air_temperature",
        "precipitation_amount",
        "relative_humidity",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required weather columns: {missing_columns}"
        )

    invalid_mask = (
        df["station_id"].isna()
        | df["station_name"].isna()
        | df["observed_at"].isna()
        | df["air_temperature"].isna()
        | df["precipitation_amount"].isna()
        | df["relative_humidity"].isna()
        | (df["relative_humidity"] < 0)
        | (df["relative_humidity"] > 100)
        | (df["precipitation_amount"] < 0)
        | (df["air_temperature"] < -30)
        | (df["air_temperature"] > 50)
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df


def validate_nta_vehicles(df):
    """Separate valid and invalid NTA vehicle records."""

    required_columns = [
        "vehicle_id",
        "trip_id",
        "route_id",
        "latitude",
        "longitude",
        "observed_at",
    ]

    # A record is invalid if a required value is missing.
    missing_required = df[required_columns].isna().any(axis=1)

    # Latitude must be between -90 and 90.
    invalid_latitude = ~df["latitude"].between(-90, 90)

    # Longitude must be between -180 and 180.
    invalid_longitude = ~df["longitude"].between(-180, 180)

    invalid_mask = (
        missing_required
        | invalid_latitude
        | invalid_longitude
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df

def validate_gtfs_routes(df):
    """Separate valid and invalid GTFS route records."""

    required_columns = [
        "route_id",
        "route_type",
    ]

    missing_required = df[required_columns].isna().any(axis=1)

    duplicate_route = df.duplicated(
        subset=["route_id"],
        keep=False,
    )

    invalid_mask = (
        missing_required
        | duplicate_route
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df

def validate_gtfs_trips(df):
    """Separate valid and invalid GTFS trip records."""

    required_columns = [
        "trip_id",
        "route_id",
        "service_id",
    ]

    missing_required = df[required_columns].isna().any(axis=1)

    duplicate_trip = df.duplicated(
        subset=["trip_id"],
        keep=False,
    )

    invalid_mask = (
        missing_required
        | duplicate_trip
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df

def validate_gtfs_stops(df):
    """Separate valid and invalid GTFS stop records."""

    required_columns = [
        "stop_id",
        "stop_name",
        "stop_lat",
        "stop_lon",
    ]

    missing_required = df[required_columns].isna().any(axis=1)

    duplicate_stop = df.duplicated(
        subset=["stop_id"],
        keep=False,
    )

    stop_lat = pd.to_numeric(
        df["stop_lat"],
        errors="coerce",
    )

    stop_lon = pd.to_numeric(
        df["stop_lon"],
        errors="coerce",
    )

    invalid_latitude = ~stop_lat.between(-90, 90)
    invalid_longitude = ~stop_lon.between(-180, 180)

    invalid_mask = (
        missing_required
        | duplicate_stop
        | invalid_latitude
        | invalid_longitude
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df

def validate_gtfs_stop_times(df):
    """Separate valid and invalid GTFS stop-time records."""

    required_columns = [
        "trip_id",
        "stop_id",
        "stop_sequence",
    ]

    missing_required = df[required_columns].isna().any(axis=1)

    stop_sequence = pd.to_numeric(
        df["stop_sequence"],
        errors="coerce",
    )

    invalid_stop_sequence = (
        stop_sequence.isna()
        | (stop_sequence < 0)
    )

    duplicate_stop_time = df.duplicated(
        subset=["trip_id", "stop_sequence"],
        keep=False,
    )

    invalid_mask = (
        missing_required
        | invalid_stop_sequence
        | duplicate_stop_time
    )

    valid_df = df[~invalid_mask].copy()
    invalid_df = df[invalid_mask].copy()

    return valid_df, invalid_df