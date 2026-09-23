SELECT
    station_id,
    observed_at,
    COUNT(*) AS observation_count
FROM {{ ref('stg_phoenix_park_weather') }}
GROUP BY
    station_id,
    observed_at
HAVING COUNT(*) > 1