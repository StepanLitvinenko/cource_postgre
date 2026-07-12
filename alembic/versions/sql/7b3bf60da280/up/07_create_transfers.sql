CREATE TABLE inventory.transfers (
    id SERIAL PRIMARY KEY,
    from_warehouse_id INTEGER NOT NULL,
    to_warehouse_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'shipping', 'in_transit', 'arrived', 'received')),
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    arriving_at TIMESTAMP WITH TIME ZONE,
    received_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_transfer_from_warehouse
        FOREIGN KEY (from_warehouse_id)
        REFERENCES catalog.warehouses(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_transfer_to_warehouse
        FOREIGN KEY (to_warehouse_id)
        REFERENCES catalog.warehouses(id)
        ON DELETE RESTRICT,

    CONSTRAINT check_warehouses_not_equal CHECK (from_warehouse_id != to_warehouse_id)
);

COMMENT ON TABLE inventory.transfers IS 'Накладные на перемещение товаров между складами';
COMMENT ON COLUMN inventory.transfers.id IS 'Уникальный идентификатор накладной';
COMMENT ON COLUMN inventory.transfers.from_warehouse_id IS 'ID склада отправления';
COMMENT ON COLUMN inventory.transfers.to_warehouse_id IS 'ID склада назначения';
COMMENT ON COLUMN inventory.transfers.status IS 'Статус накладной (planned, shipping, in_transit, arrived, received)';
COMMENT ON COLUMN inventory.transfers.total_amount IS 'Общая стоимость товаров в перемещении';
COMMENT ON COLUMN inventory.transfers.created_at IS 'Дата и время создания накладной';
COMMENT ON COLUMN inventory.transfers.started_at IS 'Дата и время начала перемещения';
COMMENT ON COLUMN inventory.transfers.arriving_at IS 'Расчетное время прибытия';
COMMENT ON COLUMN inventory.transfers.received_at IS 'Дата и время получения товаров';