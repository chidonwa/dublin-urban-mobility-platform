SELECT
    gtfs_hour,
    route_type,
    COUNT(*) AS row_count
FROM {{ ref('mart_hourly_service_summary') }}
GROUP BY
    gtfs_hour,
    route_type
HAVING COUNT(*) > 1
