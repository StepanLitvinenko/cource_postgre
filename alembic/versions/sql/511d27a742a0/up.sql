
CREATE SCHEMA IF NOT EXISTS sales;

CREATE TABLE sales.orders (
    id SERIAL PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'unpublished'
        CHECK (status IN ('unpublished', 'new', 'processing', 'pending', 'packing', 'shipped')),
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- если поддерживаем редактирование
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    warehouse_id INTEGER NOT NULL,

    CONSTRAINT fk_order_warehouse
        FOREIGN KEY (warehouse_id)
        REFERENCES catalog.warehouses(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE sales.orders IS 'Заказы';
COMMENT ON COLUMN sales.orders.id IS 'Уникальный идентификатор заказа';
COMMENT ON COLUMN sales.orders.status IS 'Статус заказа';
COMMENT ON COLUMN sales.orders.total_amount IS 'Общая сумма заказа';
COMMENT ON COLUMN sales.orders.created_at IS 'Дата и время создания заказа';
COMMENT ON COLUMN sales.orders.updated_at IS 'Дата и время последнего обновления';
COMMENT ON COLUMN sales.orders.warehouse_id IS 'ID склада отгрузки';




CREATE TABLE sales.order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_order_product UNIQUE(order_id, product_id),

    CONSTRAINT fk_order_item_order
        FOREIGN KEY (order_id)
        REFERENCES sales.orders(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_order_item_product
        FOREIGN KEY (product_id)
        REFERENCES catalog.products(id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE sales.order_items IS 'Позиции заказа';
COMMENT ON COLUMN sales.order_items.id IS 'Уникальный идентификатор позиции';
COMMENT ON COLUMN sales.order_items.order_id IS 'ID заказа';
COMMENT ON COLUMN sales.order_items.product_id IS 'ID товара';
COMMENT ON COLUMN sales.order_items.quantity IS 'Количество товара';
COMMENT ON COLUMN sales.order_items.price IS 'Цена товара на момент заказа';



