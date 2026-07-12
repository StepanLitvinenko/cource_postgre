CREATE TABLE inventory.stock (
    warehouse_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),

    PRIMARY KEY (warehouse_id, product_id),

    CONSTRAINT fk_stock_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES catalog.warehouses(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_stock_product
        FOREIGN KEY (product_id)
        REFERENCES catalog.products(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE inventory.stock IS 'Остатки товаров на складах';
COMMENT ON COLUMN inventory.stock.warehouse_id IS 'ID склада';
COMMENT ON COLUMN inventory.stock.product_id IS 'ID товара';
COMMENT ON COLUMN inventory.stock.quantity IS 'Количество товара на складе';