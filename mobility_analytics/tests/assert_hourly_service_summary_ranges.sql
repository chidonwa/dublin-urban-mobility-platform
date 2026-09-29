SELECT
    gtfs_hour,
    route_type,
    scheduled_stop_events,
    distinct_trips,
    distinct_routes
FROM {{ ref('mart_hourly_service_summary') }}
WHERE gtfs_hour < 0
   OR gtfs_hour > 47
   OR scheduled_stop_events <= 0
   OR distinct_trips <= 0
   OR distinct_routes <= 0
   OR distinct_trips > scheduled_stop_events
