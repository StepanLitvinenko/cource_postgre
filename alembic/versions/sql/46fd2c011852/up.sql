ALTER TABLE sales.orders ADD COLUMN created_by INTEGER;

DO $$
DECLARE
    default_user_id INTEGER;
BEGIN
    SELECT id INTO default_user_id
    FROM auth.users
    WHERE role = 'sales_manager'
    LIMIT 1;

    IF default_user_id IS NULL THEN
        SELECT id INTO default_user_id
        FROM auth.users
        LIMIT 1;
    END IF;

    IF default_user_id IS NOT NULL THEN
        UPDATE sales.orders SET created_by = default_user_id WHERE created_by IS NULL;
    END IF;
END $$;

ALTER TABLE sales.orders ALTER COLUMN created_by SET NOT NULL;

ALTER TABLE sales.orders
    ADD CONSTRAINT fk_order_created_by
    FOREIGN KEY (created_by)
    REFERENCES auth.users(id)
    ON DELETE RESTRICT;

COMMENT ON COLUMN sales.orders.created_by IS 'ID пользователя, создавшего заказ';