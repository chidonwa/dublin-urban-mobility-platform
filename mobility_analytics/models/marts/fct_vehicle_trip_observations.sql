{{ config(materialized='table') }}

SELECT
    v.entity_id,
    v.vehicle_id,
    v.trip_id,
    v.route_id,

    r.route_short_name,
    r.route_long_name,
    r.route_type,

    t.trip_headsign,
    t.direction_id,

    v.start_time,
    v.start_date,
    v.latitude,
    v.longitude,
    v.observed_at,
    v.ingested_at

FROM {{ ref('stg_nta_vehicle_positions') }} v

INNER JOIN {{ ref('stg_gtfs_trips') }} t
    ON v.trip_id = t.trip_id

INNER JOIN {{ ref('stg_gtfs_routes') }} r
    ON v.route_id = r.route_id

WHERE NOT (
    v.latitude = 0
    AND v.longitude = 0
)