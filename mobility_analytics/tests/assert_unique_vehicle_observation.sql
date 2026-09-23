SELECT
    vehicle_id,
    observed_at,
    COUNT(*) AS observation_count
FROM {{ ref('fct_vehicle_trip_observations') }}
GROUP BY
    vehicle_id,
    observed_at
HAVING COUNT(*) > 1