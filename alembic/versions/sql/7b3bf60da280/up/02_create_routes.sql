
CREATE TABLE inventory.routes (
    from_city_id INTEGER NOT NULL,
    to_city_id INTEGER NOT NULL,
    duration INTERVAL NOT NULL,
    total_threshold DECIMAL(10, 2) NOT NULL CHECK (total_threshold > 0),

    PRIMARY KEY (from_city_id, to_city_id),

    CONSTRAINT fk_route_from_city
        FOREIGN KEY (from_city_id)
        REFERENCES catalog.cities(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_route_to_city
        FOREIGN KEY (to_city_id)
        REFERENCES catalog.cities(id)
        ON DELETE RESTRICT,

    CONSTRAINT check_cities_not_equal CHECK (from_city_id != to_city_id)
);

COMMENT ON TABLE inventory.routes IS 'Маршруты перемещения между городами';
COMMENT ON COLUMN inventory.routes.from_city_id IS 'ID города отправления';
COMMENT ON COLUMN inventory.routes.to_city_id IS 'ID города назначения';
COMMENT ON COLUMN inventory.routes.duration IS 'Время доставки между городами';
COMMENT ON COLUMN inventory.routes.total_threshold IS 'Минимальная сумма для перемещения';