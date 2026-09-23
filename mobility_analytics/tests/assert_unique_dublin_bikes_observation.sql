select
    station_id,
    last_reported_dt,
    count(*) as observation_count
from {{ ref('stg_dublin_bikes_station_status') }}
group by
    station_id,
    last_reported_dt
having count(*) > 1