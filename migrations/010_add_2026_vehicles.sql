-- Add 2026 vehicle data by duplicating 2024 vehicles
INSERT INTO vehicles (id, year, make, model, is_custom, created_at)
SELECT 
    gen_random_uuid() as id,
    '2026' as year,
    make,
    model,
    false as is_custom,
    CURRENT_TIMESTAMP as created_at
FROM vehicles 
WHERE year = '2024'; 