-- Таблица: inventory.transfer_items
CREATE TABLE inventory.transfer_items (
    id SERIAL PRIMARY KEY,
    transfer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    reserve_id INTEGER,
    requested_by INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'shipped', 'received')),

    CONSTRAINT fk_transfer_item_transfer
        FOREIGN KEY (transfer_id)
        REFERENCES inventory.transfers(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_transfer_item_product
        FOREIGN KEY (product_id)
        REFERENCES catalog.products(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_transfer_item_reserve
        FOREIGN KEY (reserve_id)
        REFERENCES inventory.reserves(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_transfer_item_requested_by
        FOREIGN KEY (requested_by)
        REFERENCES auth.users(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE inventory.transfer_items IS 'Позиции накладной на перемещение';
COMMENT ON COLUMN inventory.transfer_items.id IS 'Уникальный идентификатор позиции';
COMMENT ON COLUMN inventory.transfer_items.transfer_id IS 'ID накладной';
COMMENT ON COLUMN inventory.transfer_items.product_id IS 'ID товара';
COMMENT ON COLUMN inventory.transfer_items.quantity IS 'Количество товара';
COMMENT ON COLUMN inventory.transfer_items.reserve_id IS 'ID резерва (если перемещение для заказа)';
COMMENT ON COLUMN inventory.transfer_items.requested_by IS 'ID пользователя, запросившего перемещение';
COMMENT ON COLUMN inventory.transfer_items.status IS 'Статус позиции (planned, shipped, received)';