with source as (

    select *
    from {{ source('raw', 'gtfs_stops') }}

),

renamed as (

    select
        stop_id,
        stop_code,
        stop_name,
        stop_desc,
        stop_lat,
        stop_lon,
        zone_id,
        stop_url,
        location_type,
        parent_station

    from source

)

select *
from renamed