ALTER TABLE sales.orders ADD COLUMN created_by INTEGER;

ALTER TABLE sales.orders
    ADD CONSTRAINT fk_order_created_by
    FOREIGN KEY (created_by)
    REFERENCES auth.users(id)
    ON DELETE RESTRICT;

COMMENT ON COLUMN sales.orders.created_by IS 'ID пользователя, создавшего заказ';