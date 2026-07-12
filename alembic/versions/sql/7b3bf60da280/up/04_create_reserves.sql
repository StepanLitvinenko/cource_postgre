CREATE TABLE inventory.reserves (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_reserve_order
        FOREIGN KEY (order_id)
        REFERENCES sales.orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reserve_product
        FOREIGN KEY (product_id)
        REFERENCES catalog.products(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_reserve_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES catalog.warehouses(id)
        ON DELETE RESTRICT,

    CONSTRAINT unique_order_product_warehouse UNIQUE (order_id, product_id, warehouse_id)
);

COMMENT ON TABLE inventory.reserves IS 'Резервы товаров под заказы';
COMMENT ON COLUMN inventory.reserves.id IS 'Уникальный идентификатор резерва';
COMMENT ON COLUMN inventory.reserves.order_id IS 'ID заказа';
COMMENT ON COLUMN inventory.reserves.product_id IS 'ID товара';
COMMENT ON COLUMN inventory.reserves.warehouse_id IS 'ID склада';
COMMENT ON COLUMN inventory.reserves.quantity IS 'Зарезервированное количество';
COMMENT ON COLUMN inventory.reserves.created_at IS 'Дата и время создания резерва';
COMMENT ON COLUMN inventory.reserves.updated_at IS 'Дата и время последнего обновления';