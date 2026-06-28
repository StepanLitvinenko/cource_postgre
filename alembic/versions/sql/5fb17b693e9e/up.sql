
CREATE SCHEMA IF NOT EXISTS catalog;

CREATE TABLE catalog.product_categories (
    id SERIAL PRIMARY KEY,
    category_type TEXT NOT NULL UNIQUE
);

COMMENT ON TABLE catalog.product_categories IS 'Категории товаров';
COMMENT ON COLUMN catalog.product_categories.id IS 'Уникальный идентификатор категории';
COMMENT ON COLUMN catalog.product_categories.category_type IS 'Название категории';

CREATE TABLE catalog.products (
    id SERIAL PRIMARY KEY,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    category_id INTEGER NOT NULL,

    -- Внешний ключ к категории с ограничением на удаление
    CONSTRAINT fk_product_category
        FOREIGN KEY (category_id)
        REFERENCES catalog.product_categories(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE catalog.products IS 'Товары';
COMMENT ON COLUMN catalog.products.id IS 'Уникальный идентификатор товара';
COMMENT ON COLUMN catalog.products.sku IS 'Артикул товара (уникальный)';
COMMENT ON COLUMN catalog.products.name IS 'Название товара';
COMMENT ON COLUMN catalog.products.price IS 'Цена товара (должна быть > 0)';
COMMENT ON COLUMN catalog.products.category_id IS 'ID категории товара';




CREATE TABLE catalog.warehouses (
    id SERIAL PRIMARY KEY,
    city TEXT NOT NULL,
    address TEXT NOT NULL,
    is_central BOOLEAN NOT NULL DEFAULT false,
    label TEXT
    );

COMMENT ON TABLE catalog.warehouses IS 'Склады';
COMMENT ON COLUMN catalog.warehouses.id IS 'Уникальный идентификатор склада';
COMMENT ON COLUMN catalog.warehouses.city IS 'Город расположения склада';
COMMENT ON COLUMN catalog.warehouses.address IS 'Адрес склада';
COMMENT ON COLUMN catalog.warehouses.is_central IS 'Признак центрального склада, только один может быть';
COMMENT ON COLUMN catalog.warehouses.label IS 'Метка/название склада';


CREATE UNIQUE INDEX unique_central_warehouse
    ON catalog.warehouses (is_central)
    WHERE is_central = true;

