select
    station_id,
    station_name,
    county,
    observed_at,
    air_pressure,
    air_temperature,
    precipitation_amount,
    relative_humidity,
    ingested_at
from {{ source('raw', 'phoenix_park_weather') }}