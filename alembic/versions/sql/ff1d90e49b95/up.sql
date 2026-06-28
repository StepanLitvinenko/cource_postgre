ALTER SCHEMA catalog OWNER TO catalog_manager;

ALTER SCHEMA sales OWNER TO sales_manager;

ALTER TABLE catalog.product_categories OWNER TO catalog_manager;
ALTER TABLE catalog.products OWNER TO catalog_manager;
ALTER TABLE catalog.warehouses OWNER TO catalog_manager;

ALTER TABLE sales.orders OWNER TO sales_manager;
ALTER TABLE sales.order_items OWNER TO sales_manager;

ALTER SEQUENCE catalog.product_categories_id_seq OWNER TO catalog_manager;
ALTER SEQUENCE catalog.products_id_seq OWNER TO catalog_manager;
ALTER SEQUENCE catalog.warehouses_id_seq OWNER TO catalog_manager;
ALTER SEQUENCE sales.orders_id_seq OWNER TO sales_manager;


GRANT ALL PRIVILEGES ON SCHEMA catalog TO catalog_manager;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA catalog TO catalog_manager;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA catalog TO catalog_manager;

GRANT CREATE ON SCHEMA catalog TO catalog_manager;


GRANT ALL PRIVILEGES ON SCHEMA sales TO sales_manager;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sales TO sales_manager;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sales TO sales_manager;

GRANT CREATE ON SCHEMA sales TO sales_manager;

GRANT USAGE ON SCHEMA catalog TO sales_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA catalog TO sales_manager;


GRANT USAGE ON SCHEMA catalog TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA catalog TO PUBLIC;

ALTER DEFAULT PRIVILEGES FOR ROLE catalog_manager IN SCHEMA catalog
    GRANT ALL PRIVILEGES ON TABLES TO catalog_manager;

ALTER DEFAULT PRIVILEGES FOR ROLE catalog_manager IN SCHEMA catalog
    GRANT ALL PRIVILEGES ON SEQUENCES TO catalog_manager;

ALTER DEFAULT PRIVILEGES FOR ROLE sales_manager IN SCHEMA sales
    GRANT ALL PRIVILEGES ON TABLES TO sales_manager;

ALTER DEFAULT PRIVILEGES FOR ROLE sales_manager IN SCHEMA sales
    GRANT ALL PRIVILEGES ON SEQUENCES TO sales_manager;

ALTER DEFAULT PRIVILEGES IN SCHEMA catalog
    GRANT SELECT ON TABLES TO PUBLIC;

ALTER DEFAULT PRIVILEGES IN SCHEMA catalog
    GRANT USAGE ON SEQUENCES TO PUBLIC;

ALTER DEFAULT PRIVILEGES IN SCHEMA catalog
    GRANT SELECT ON TABLES TO sales_manager;


GRANT catalog_manager TO supervisor;
GRANT sales_manager TO supervisor;

