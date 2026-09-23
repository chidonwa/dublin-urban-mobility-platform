SELECT
    vehicle_id,
    observed_at,
    COUNT(*) AS observation_count
FROM {{ ref('stg_nta_vehicle_positions') }}
GROUP BY
    vehicle_id,
    observed_at
HAVING COUNT(*) > 1