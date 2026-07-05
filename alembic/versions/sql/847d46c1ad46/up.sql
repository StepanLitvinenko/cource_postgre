
CREATE TABLE catalog.cities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);



INSERT INTO catalog.cities (name) VALUES
    ('Москва'),
    ('Санкт-Петербург'),
    ('Новосибирск'),
    ('Екатеринбург'),
    ('Казань'),
    ('Нижний Новгород'),
    ('Челябинск'),
    ('Самара'),
    ('Омск'),
    ('Ростов-на-Дону'),
    ('Уфа'),
    ('Красноярск'),
    ('Воронеж'),
    ('Пермь'),
    ('Волгоград');



ALTER TABLE catalog.warehouses ADD COLUMN city_id INTEGER;

UPDATE catalog.warehouses w
SET city_id = c.id
FROM catalog.cities c
WHERE w.city = c.name;

ALTER TABLE catalog.warehouses ALTER COLUMN city_id SET NOT NULL;

ALTER TABLE catalog.warehouses
    ADD CONSTRAINT fk_warehouse_city
    FOREIGN KEY (city_id)
    REFERENCES catalog.cities(id)
    ON DELETE RESTRICT;

ALTER TABLE catalog.warehouses DROP COLUMN city;

COMMENT ON COLUMN catalog.warehouses.city_id IS 'ID города в котором расположен скалд';