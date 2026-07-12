CREATE TABLE inventory.delivery_items (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'shipped')),

    CONSTRAINT fk_delivery_item_delivery
        FOREIGN KEY (delivery_id)
        REFERENCES inventory.deliveries(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_delivery_item_product
        FOREIGN KEY (product_id)
        REFERENCES catalog.products(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE inventory.delivery_items IS 'Позиции накладной на доставку';
COMMENT ON COLUMN inventory.delivery_items.id IS 'Уникальный идентификатор позиции';
COMMENT ON COLUMN inventory.delivery_items.delivery_id IS 'ID накладной';
COMMENT ON COLUMN inventory.delivery_items.product_id IS 'ID товара';
COMMENT ON COLUMN inventory.delivery_items.quantity IS 'Количество товара';
COMMENT ON COLUMN inventory.delivery_items.status IS 'Статус позиции (planned, shipped)';