
ALTER TABLE sales.orders DROP CONSTRAINT IF EXISTS fk_order_created_by;
ALTER TABLE sales.orders DROP COLUMN IF EXISTS created_by;