-- ============================================================
-- NTA Static GTFS Data Quality Checks
-- ============================================================
-- These queries validate the integrity and quality of the
-- static GTFS data loaded into the raw PostgreSQL schema.
-- ============================================================


-- 1. Check that every trip references an existing route.

SELECT COUNT(*) AS trips_without_route
FROM raw.gtfs_trips AS t
LEFT JOIN raw.gtfs_routes AS r
    ON t.route_id = r.route_id
WHERE r.route_id IS NULL;


-- 2. Check that every stop-time record references an existing trip.

SELECT COUNT(*) AS stop_times_without_trip
FROM raw.gtfs_stop_times AS st
LEFT JOIN raw.gtfs_trips AS t
    ON st.trip_id = t.trip_id
WHERE t.trip_id IS NULL;


-- 3. Check that every stop-time record references an existing stop.

SELECT COUNT(*) AS stop_times_without_stop
FROM raw.gtfs_stop_times AS st
LEFT JOIN raw.gtfs_stops AS s
    ON st.stop_id = s.stop_id
WHERE s.stop_id IS NULL;

-- 4. Check for duplicate stop-time keys.
-- A trip should have only one record for each stop sequence.

SELECT COUNT(*) AS duplicate_stop_time_keys
FROM (
    SELECT
        trip_id,
        stop_sequence
    FROM raw.gtfs_stop_times
    GROUP BY
        trip_id,
        stop_sequence
    HAVING COUNT(*) > 1
) AS duplicates;


-- 5. Check for missing critical stop-time values.

SELECT
    COUNT(*) FILTER (
        WHERE trip_id IS NULL
    ) AS missing_trip_id,

    COUNT(*) FILTER (
        WHERE stop_id IS NULL
    ) AS missing_stop_id,

    COUNT(*) FILTER (
        WHERE stop_sequence IS NULL
    ) AS missing_stop_sequence

FROM raw.gtfs_stop_times;

-- 6. Check that arrival and departure times use HH:MM:SS format.
-- GTFS permits hours greater than 23 for services after midnight.

SELECT COUNT(*) AS invalid_time_formats
FROM raw.gtfs_stop_times
WHERE
    (
        arrival_time IS NOT NULL
        AND arrival_time !~ '^[0-9]{2}:[0-9]{2}:[0-9]{2}$'
    )
    OR
    (
        departure_time IS NOT NULL
        AND departure_time !~ '^[0-9]{2}:[0-9]{2}:[0-9]{2}$'
    );


-- 7. Check that minutes and seconds are valid.
-- Hours are intentionally not restricted to 0-23 because
-- GTFS supports times after midnight such as 24:21:00.

SELECT COUNT(*) AS invalid_time_values
FROM raw.gtfs_stop_times
WHERE
    (
        arrival_time IS NOT NULL
        AND (
            SPLIT_PART(arrival_time, ':', 2)::INTEGER > 59
            OR SPLIT_PART(arrival_time, ':', 3)::INTEGER > 59
        )
    )
    OR
    (
        departure_time IS NOT NULL
        AND (
            SPLIT_PART(departure_time, ':', 2)::INTEGER > 59
            OR SPLIT_PART(departure_time, ':', 3)::INTEGER > 59
        )
    );