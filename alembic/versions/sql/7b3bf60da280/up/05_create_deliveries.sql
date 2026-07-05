CREATE TABLE inventory.deliveries (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL UNIQUE,
    warehouse_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'shipping', 'shipped')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_delivery_order
        FOREIGN KEY (order_id)
        REFERENCES sales.orders(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_delivery_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES catalog.warehouses(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE inventory.deliveries IS 'Накладные на доставку заказов';
COMMENT ON COLUMN inventory.deliveries.id IS 'Уникальный идентификатор накладной';
COMMENT ON COLUMN inventory.deliveries.order_id IS 'ID заказа';
COMMENT ON COLUMN inventory.deliveries.warehouse_id IS 'ID склада отправления';
COMMENT ON COLUMN inventory.deliveries.status IS 'Статус накладной (planned, shipping, shipped)';
COMMENT ON COLUMN inventory.deliveries.created_at IS 'Дата и время создания накладной';
COMMENT ON COLUMN inventory.deliveries.shipped_at IS 'Дата и время отгрузки';