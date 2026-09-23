SELECT
    v.vehicle_id,
    v.trip_id,
    v.route_id AS realtime_route_id,
    t.route_id AS gtfs_route_id,
    v.observed_at
FROM {{ ref('stg_nta_vehicle_positions') }} v
INNER JOIN {{ ref('stg_gtfs_trips') }} t
    ON v.trip_id = t.trip_id
WHERE v.route_id <> t.route_id