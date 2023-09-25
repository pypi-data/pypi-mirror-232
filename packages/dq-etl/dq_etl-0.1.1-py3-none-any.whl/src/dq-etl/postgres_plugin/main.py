from plugin import PostgresPlugin

if __name__ == "__main__":
    # Set up database credentials.
    HOST = "localhost"
    PORT = 5432
    USER = "postgres"
    PASSWORD = "mysecretpassword"
    DBNAME = "pgbench"
    TABLE_NAME = "pgbench_accounts"

    # Initialize the plugin and connect to the database.
    plugin = PostgresPlugin(host=HOST, port=PORT, user=USER, password=PASSWORD, dbname=DBNAME)
    plugin.connect()

    # Extract and print metadata for the "pgbench_accounts" table.
    metadata = plugin.extract_metadata(table_name=TABLE_NAME)
    for column, data_type in metadata:
        print(f"{column}: {data_type}")

    # Extract data and convert it to Apache Arrow format.
    arrow_table = plugin.extract_data_to_arrow(table_name=TABLE_NAME)
    print("\nFirst 10 rows of the Arrow table:")
    print(arrow_table.to_pandas().head(10))  # Convert to Pandas DataFrame for easy printing.

    # Don't forget to disconnect after operations!
    plugin.disconnect()
