

GRANT USAGE ON SCHEMA inventory TO inventory_manager;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA inventory TO inventory_manager;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA inventory TO inventory_manager;
GRANT CREATE ON SCHEMA inventory TO inventory_manager;



GRANT USAGE ON SCHEMA inventory TO worker;


GRANT ALL PRIVILEGES ON TABLE inventory.stock TO worker;

GRANT SELECT, UPDATE ON TABLE inventory.reserves TO worker;

GRANT SELECT, UPDATE ON TABLE inventory.deliveries TO worker;
GRANT SELECT, UPDATE ON TABLE inventory.delivery_items TO worker;

GRANT SELECT, UPDATE ON TABLE inventory.transfers TO worker;
GRANT SELECT, UPDATE ON TABLE inventory.transfer_items TO worker;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA inventory TO worker;