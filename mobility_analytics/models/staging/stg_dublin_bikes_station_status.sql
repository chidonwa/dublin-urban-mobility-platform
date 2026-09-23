select
    id,
    station_id,
    name as station_name,
    address,
    latitude,
    longitude,
    capacity,
    num_bikes_available,
    num_docks_available,
    is_installed,
    is_renting,
    is_returning,
    last_reported_dt,
    ingested_at
from {{ source('raw', 'dublin_bikes_station_status') }}