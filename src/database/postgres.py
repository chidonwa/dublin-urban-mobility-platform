import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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
    """Load new records from a pandas DataFrame into PostgreSQL."""

    engine = get_database_engine()

    # For Dublin Bikes station observations, remove records that
    # already exist in PostgreSQL.
    if table_name == "dublin_bikes_station_status":
        query = text(
            f"""
            SELECT station_id, last_reported_dt
            FROM {schema}.{table_name}
            """
        )

        with engine.connect() as connection:
            existing_records = connection.execute(query).fetchall()

        existing_keys = {
            (str(row.station_id), row.last_reported_dt)
            for row in existing_records
        }

        is_new = df.apply(
            lambda row: (
                str(row["station_id"]),
                row["last_reported_dt"],
            ) not in existing_keys,
            axis=1,
        )

        df_to_load = df[is_new].copy()

        skipped = len(df) - len(df_to_load)

        print(f"New records to load: {len(df_to_load)}")
        print(f"Duplicate records skipped: {skipped}")

        if df_to_load.empty:
            print("No new records to load into PostgreSQL.")
            return

    else:
        df_to_load = df

    df_to_load.to_sql(
        name=table_name,
        con=engine,
        schema=schema,
        if_exists=if_exists,
        index=False,
        method="multi",
    )

    print(f"Loaded {len(df_to_load)} new records into PostgreSQL.")