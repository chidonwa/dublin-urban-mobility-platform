SELECT
    station_id,
    station_name,
    observation_count,
    avg_bike_availability_pct,
    avg_dock_availability_pct,
    empty_station_observations,
    full_station_observations
FROM {{ ref('mart_bike_station_summary') }}
WHERE observation_count <= 0

    OR avg_bike_availability_pct < 0
    OR avg_bike_availability_pct > 100

    OR avg_dock_availability_pct < 0
    OR avg_dock_availability_pct > 100

    OR empty_station_observations < 0
    OR empty_station_observations > observation_count

    OR full_station_observations < 0
    OR full_station_observations > observation_count