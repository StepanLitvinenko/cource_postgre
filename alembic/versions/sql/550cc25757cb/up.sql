
ALTER TABLE sales.order_items ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

COMMENT ON COLUMN sales.order_items.updated_at IS 'Дата и время последнего обновления позиции';