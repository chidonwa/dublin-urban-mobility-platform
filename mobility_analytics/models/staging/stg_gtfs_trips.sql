with source as (

    select *
    from {{ source('raw', 'gtfs_trips') }}

),

renamed as (

    select
        trip_id,
        route_id,
        service_id,
        trip_headsign,
        trip_short_name,
        direction_id,
        block_id,
        shape_id

    from source

)

select *
from renamed