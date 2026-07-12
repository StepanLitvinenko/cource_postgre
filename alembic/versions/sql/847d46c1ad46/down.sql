ALTER TABLE catalog.warehouses ADD COLUMN city TEXT;

UPDATE catalog.warehouses w
SET city = c.name
FROM catalog.cities c
WHERE w.city_id = c.id;

ALTER TABLE catalog.warehouses ALTER COLUMN city SET NOT NULL;

ALTER TABLE catalog.warehouses DROP CONSTRAINT IF EXISTS fk_warehouse_city;

ALTER TABLE catalog.warehouses DROP COLUMN city_id;

DROP TABLE IF EXISTS catalog.cities CASCADE;