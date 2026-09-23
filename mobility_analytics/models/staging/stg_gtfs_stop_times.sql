with source as (

    select *
    from {{ source('raw', 'gtfs_stop_times') }}

),

renamed as (

    select
        trip_id,
        arrival_time,
        departure_time,
        stop_id,
        stop_sequence,
        stop_headsign,
        pickup_type,
        drop_off_type,
        timepoint

    from source

)

select *
from renamed