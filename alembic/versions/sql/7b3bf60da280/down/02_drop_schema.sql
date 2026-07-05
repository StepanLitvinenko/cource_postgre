DROP SCHEMA IF EXISTS inventory CASCADE;

DO $$
BEGIN
    RAISE NOTICE 'Миграция откачена: схема inventory удалена';
END $$;