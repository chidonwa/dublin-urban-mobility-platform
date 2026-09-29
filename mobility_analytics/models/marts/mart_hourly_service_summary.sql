{{ config(materialized='table') }}

SELECT
    SPLIT_PART(st.arrival_time, ':', 1)::integer AS gtfs_hour,
    r.route_type,

    CASE
        WHEN r.route_type = 0 THEN 'Tram / Light Rail'
        WHEN r.route_type = 2 THEN 'Rail'
        WHEN r.route_type = 3 THEN 'Bus'
        ELSE 'Other'
    END AS transport_mode,

    COUNT(*) AS scheduled_stop_events,
    COUNT(DISTINCT st.trip_id) AS distinct_trips,
    COUNT(DISTINCT t.route_id) AS distinct_routes

FROM {{ ref('stg_gtfs_stop_times') }} st

JOIN {{ ref('stg_gtfs_trips') }} t
    ON st.trip_id = t.trip_id

JOIN {{ ref('stg_gtfs_routes') }} r
    ON t.route_id = r.route_id

WHERE st.arrival_time IS NOT NULL

GROUP BY
    SPLIT_PART(st.arrival_time, ':', 1)::integer,
    r.route_type

ORDER BY
    gtfs_hour,
    route_type
