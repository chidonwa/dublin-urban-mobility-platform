with stop_services as (

    select
        stop_times.stop_id,
        trips.route_id,
        routes.route_type,
        stop_times.trip_id

    from {{ ref('stg_gtfs_stop_times') }} as stop_times

    inner join {{ ref('stg_gtfs_trips') }} as trips
        on stop_times.trip_id = trips.trip_id

    inner join {{ ref('stg_gtfs_routes') }} as routes
        on trips.route_id = routes.route_id
),

stop_summary as (

    select
        stop_id,
        count(*) as scheduled_stop_events,
        count(distinct trip_id) as distinct_trips,
        count(distinct route_id) as distinct_routes,
        count(distinct route_type) as transport_modes

    from stop_services

    group by stop_id
)

select
    stops.stop_id,
    stops.stop_name,
    stops.stop_lat,
    stops.stop_lon,
    coalesce(summary.scheduled_stop_events, 0) as scheduled_stop_events,
    coalesce(summary.distinct_trips, 0) as distinct_trips,
    coalesce(summary.distinct_routes, 0) as distinct_routes,
    coalesce(summary.transport_modes, 0) as transport_modes

from {{ ref('stg_gtfs_stops') }} as stops

left join stop_summary as summary
    on stops.stop_id = summary.stop_id