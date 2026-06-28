

CREATE SCHEMA IF NOT EXISTS auth;

COMMENT ON SCHEMA auth IS 'Схема для аутентификации и пользователей';



CREATE EXTENSION IF NOT EXISTS pgcrypto;



CREATE TABLE auth.users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('catalog_manager', 'sales_manager')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE auth.users IS 'Пользователи системы';
COMMENT ON COLUMN auth.users.id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN auth.users.username IS 'Имя пользователя (уникальное)';
COMMENT ON COLUMN auth.users.password IS 'Хэш пароля (используется pgcrypto)';
COMMENT ON COLUMN auth.users.role IS 'Роль пользователя (catalog_manager или sales_manager)';
COMMENT ON COLUMN auth.users.created_at IS 'Дата и время создания';
COMMENT ON COLUMN auth.users.updated_at IS 'Дата и время последнего обновления';


GRANT USAGE ON SCHEMA auth TO PUBLIC;
GRANT SELECT ON auth.users TO PUBLIC;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA auth TO catalog_manager;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA auth TO catalog_manager;


GRANT USAGE ON SCHEMA auth TO sales_manager;
GRANT SELECT ON auth.users TO sales_manager;


ALTER DEFAULT PRIVILEGES IN SCHEMA auth
    GRANT SELECT ON TABLES TO PUBLIC;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth
    GRANT ALL PRIVILEGES ON TABLES TO catalog_manager;

ALTER DEFAULT PRIVILEGES IN SCHEMA auth
    GRANT ALL PRIVILEGES ON SEQUENCES TO catalog_manager;


-- Пароли: cat_man/cat_pass, sale_man/sale_pass
INSERT INTO auth.users (username, password, role)
VALUES
    ('cat_man', crypt('cat_pass', gen_salt('bf')), 'catalog_manager'),
    ('sale_man', crypt('sale_pass', gen_salt('bf')), 'sales_manager')
ON CONFLICT (username) DO NOTHING;