SELECT
    vehicle_id,
    trip_id,
    route_id,
    latitude,
    longitude,
    observed_at
FROM {{ ref('fct_vehicle_trip_observations') }}
WHERE latitude NOT BETWEEN -90 AND 90
    OR longitude NOT BETWEEN -180 AND 180
    OR (latitude = 0 AND longitude = 0)