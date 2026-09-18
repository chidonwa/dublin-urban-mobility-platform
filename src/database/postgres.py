import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert


load_dotenv()


def get_database_engine():
    """Create and return a PostgreSQL SQLAlchemy engine."""

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD", "")

    database_url = (
        f"postgresql+psycopg://{user}:{password}"
        f"@{host}:{port}/{database}"
    )

    return create_engine(database_url)


def load_dataframe_to_postgres(
    df,
    table_name,
    schema="raw",
    if_exists="append",
):
    """Load records into PostgreSQL while skipping duplicates."""

    engine = get_database_engine()

    if df.empty:
        print("No records to load into PostgreSQL.")
        return

    # Dublin Bikes observations are uniquely identified by
    # station ID and the time reported by the source.
    if table_name == "dublin_bikes_station_status":
        conflict_columns = [
            "station_id",
            "last_reported_dt",
        ]

    # Phoenix Park weather observations are uniquely identified
    # by station ID and observation time.
    elif table_name == "phoenix_park_weather":
        conflict_columns = [
            "station_id",
            "observed_at",
        ]

    elif table_name == "nta_vehicle_positions":
        conflict_columns = [
            "vehicle_id",
            "observed_at",
        ]

    # For tables without duplicate-handling rules,
    # use the normal pandas loading method.
    else:
        df.to_sql(
            name=table_name,
            con=engine,
            schema=schema,
            if_exists=if_exists,
            index=False,
            method="multi",
        )

        print(f"Loaded {len(df)} records into PostgreSQL.")
        return

    # Read the existing PostgreSQL table structure.
    metadata = MetaData()

    table = Table(
        table_name,
        metadata,
        schema=schema,
        autoload_with=engine,
    )

    # Convert the DataFrame into records that SQLAlchemy can insert.
    records = df.to_dict(orient="records")

    # Build the PostgreSQL INSERT statement.
    statement = insert(table).values(records)

    # If the unique station/timestamp combination already exists,
    # PostgreSQL skips that record instead of raising an error.
    statement = statement.on_conflict_do_nothing(
        index_elements=conflict_columns
    ).returning(*[table.c[column] for column in conflict_columns])

    # engine.begin() automatically commits if the operation succeeds
    # and rolls back if an error occurs.
    with engine.begin() as connection:
        result = connection.execute(statement)
        inserted_rows = result.fetchall()

    inserted = len(inserted_rows)
    skipped = len(df) - inserted

    print(f"New records loaded: {inserted}")
    print(f"Duplicate records skipped: {skipped}")