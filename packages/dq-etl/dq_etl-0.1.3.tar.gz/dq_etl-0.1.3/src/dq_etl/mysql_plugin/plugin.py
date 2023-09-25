import mysql.connector
import pandas as pd
import pyarrow as pa
from .type_mapping import PYARROW_TO_MYSQL_MAP, MYSQL_TO_PYARROW_MAP

class MySQLPlugin:
    def __init__(self, host, port, user, password, dbname, **kwargs):
        self.connection_string = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': dbname,
            'charset': 'utf8mb4'
        }
        self.connection = None

    def connect(self):
        if not self.connection:
            self.connection = mysql.connector.connect(**self.connection_string)

    def extract_metadata(self, table_name):
        """Retrieve the metadata (column names and types) for the given table."""
        cursor = self.connection.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        metadata = [(row[0], (row[1] if isinstance(row[1], str) else row[1].decode('utf-8')).split('(')[0].upper()) for row in cursor.fetchall()]
        cursor.close()
        return metadata

    
    def get_total_records(self, table_name):
        """Retrieve the total number of records in the given table."""
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_records = cursor.fetchone()[0]
        cursor.close()
        return total_records
    
    def plugin_reader(self, table_name, batch_size, offset=0):
        total_rows = self.get_total_records(table_name)
        
        while offset < total_rows:
            with self.connection.cursor() as cursor:
                query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
                cursor.execute(query)
                data = cursor.fetchall()
                
                # No data means, no further records for the current batch size.
                if not data:
                    break
                    
                columns = [desc[0] for desc in cursor.description]
                metadata = self.extract_metadata(table_name)
                pyarrow_types = [MYSQL_TO_PYARROW_MAP[mysql_type] for _, mysql_type in metadata]
                
                transposed_data = list(zip(*data))
                arrays = [pa.array(col_data, type=pa_type) for col_data, pa_type in zip(transposed_data, pyarrow_types)]
                
                table = pa.table({col: arr for col, arr in zip(columns, arrays)})

                yield table

                # Move to the next batch
                offset += batch_size

    def _create_table_if_not_exists(self, table, target_table_name):
        """Create the table in MySQL based on PyArrow Table schema if it doesn't already exist."""
        # Get column names and types from the PyArrow table
        df = table.to_pandas()
        column_names = df.columns
        column_types = [PYARROW_TO_MYSQL_MAP[str(dtype)] for dtype in df.dtypes]

        columns_sql = ", ".join([f"{col} {sql_type}" for col, sql_type in zip(column_names, column_types)])
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {target_table_name} ({columns_sql});"
        
        cursor = self.connection.cursor()
        cursor.execute(create_table_sql)
        cursor.close()

    def plugin_writer(self, table, target_table_name):
        """Write the given PyArrow Table data to the specified MySQL table."""
        avg_row_size = 1000  
        max_packet = self.get_max_allowed_packet()
        batch_size = max_packet // avg_row_size

        # Create the table if it doesn't exist
        self._create_table_if_not_exists(table, target_table_name)

        # Convert PyArrow Table to DataFrame
        df = table.to_pandas()

        # Bulk insert data in chunks to avoid 'max_allowed_packet' error
        cursor = self.connection.cursor()

        # Use placeholders to prevent SQL injection
        placeholders = ", ".join(["%s"] * len(df.columns))
        columns = ", ".join(df.columns)
        insert_sql = f"INSERT INTO {target_table_name} ({columns}) VALUES ({placeholders})"
        
        # Splitting the dataframe into smaller chunks and inserting each chunk
        for start in range(0, len(df), batch_size):
            end = start + batch_size
            df_chunk = df.iloc[start:end]
            cursor.executemany(insert_sql, df_chunk.values.tolist())
            self.connection.commit()
        
        cursor.close()

 
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_max_allowed_packet(self):
        """Retrieve the max_allowed_packet value from MySQL."""
        cursor = self.connection.cursor()
        cursor.execute("SHOW VARIABLES LIKE 'max_allowed_packet'")
        result = cursor.fetchone()
        cursor.close()
        return int(result[1])  # Convert the result to an integer

