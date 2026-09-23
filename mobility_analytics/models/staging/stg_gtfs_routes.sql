with source as (

    select *
    from {{ source('raw', 'gtfs_routes') }}

),

renamed as (

    select
        route_id,
        agency_id,
        route_short_name,
        route_long_name,
        route_desc,
        route_type,
        route_url,
        route_color,
        route_text_color

    from source

)

select *
from renamed