
DROP TABLE IF EXISTS catalog.products CASCADE;
DROP TABLE IF EXISTS catalog.product_categories CASCADE;
DROP TABLE IF EXISTS catalog.warehouses CASCADE;

DROP SCHEMA IF EXISTS catalog CASCADE;

DO $$
BEGIN
    RAISE NOTICE 'Миграция откачена: все таблицы в схеме catalog удалены';
END $$;