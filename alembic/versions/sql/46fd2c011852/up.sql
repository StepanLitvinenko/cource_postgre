ALTER TABLE sales.orders ADD COLUMN created_by INTEGER;

UPDATE sales.orders SET created_by = 1 WHERE created_by IS NULL;


ALTER TABLE sales.orders ALTER COLUMN created_by SET NOT NULL;

ALTER TABLE sales.orders
    ADD CONSTRAINT fk_order_created_by
    FOREIGN KEY (created_by)
    REFERENCES auth.users(id)
    ON DELETE RESTRICT;

COMMENT ON COLUMN sales.orders.created_by IS 'ID пользователя, создавшего заказ';