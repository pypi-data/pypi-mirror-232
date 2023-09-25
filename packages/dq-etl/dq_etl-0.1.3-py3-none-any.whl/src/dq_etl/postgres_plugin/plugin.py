import psycopg2
import pyarrow as pa
from .type_mapping import POSTGRES_TO_PYARROW_MAP, PYARROW_TO_POSTGRES_MAP

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PostgresPlugin:

    def __init__(self, host, port, user, password, dbname, **kwargs):
        self.connection_string = f"dbname='{dbname}' user='{user}' host='{host}' password='{password}' port='{port}'"
        self.connection = None

    def connect(self):
        self.connection = psycopg2.connect(self.connection_string)

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def extract_metadata(self, table_name):
        # Example: Extract column names and types for a table.
        with self.connection.cursor() as cursor:
            query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'"
            cursor.execute(query)
            metadata = cursor.fetchall()
        return metadata

    def extract_data_to_arrow(self, table_name):
        # Extract the data and convert to Arrow format.
        with self.connection.cursor() as cursor:
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            data = cursor.fetchall()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]

            # Get data types from PostgreSQL and map them to PyArrow types
            metadata = self.extract_metadata(table_name)
            pyarrow_types = [POSTGRES_TO_PYARROW_MAP[pg_type] for _, pg_type in metadata]
            
            # Transpose data rows to align with columns
            transposed_data = list(zip(*data))
            
            # Convert data to Arrow table with correct types
            arrays = [pa.array(col_data, type=pa_type) for col_data, pa_type in zip(transposed_data, pyarrow_types)]
            table = pa.table({col: arr for col, arr in zip(columns, arrays)})

        return table
    
    
    def plugin_reader(self, table_name, batch_size, offset=0):
        total_rows = self.get_total_records(table_name)
        
        while offset < total_rows:
            with self.connection.cursor() as cursor:
                query = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
                cursor.execute(query)
                data = cursor.fetchall()
                
                # No data means, no further records for the current batch size. Break and let dynamic_batch_generator decide what to do next
                if not data:
                    break
                    
                columns = [desc[0] for desc in cursor.description]
                metadata = self.extract_metadata(table_name)
                pyarrow_types = [POSTGRES_TO_PYARROW_MAP[pg_type] for _, pg_type in metadata]
                transposed_data = list(zip(*data))
                arrays = [pa.array(col_data, type=pa_type) for col_data, pa_type in zip(transposed_data, pyarrow_types)]
                table = pa.table({col: arr for col, arr in zip(columns, arrays)})

                yield table

                # Move to the next batch
                offset += batch_size

    def plugin_writer(self, table, target_table_name):
        """Write the given PyArrow Table data to the specified PostgreSQL table."""
        try:
            # Convert PyArrow Table to DataFrame
            df = table.to_pandas()

            # Using the DataFrame.to_sql method in combination with SQLAlchemy
            from sqlalchemy import create_engine
            engine = create_engine(f'postgresql+psycopg2://{self.connection_string}')

            # Infer PostgreSQL datatypes from PyArrow table datatypes
            dtype_mapping = {}
            for column, dtype in zip(df.columns, df.dtypes):
                try:
                    pg_type = PYARROW_TO_POSTGRES_MAP[str(dtype)]
                    dtype_mapping[column] = pg_type
                except KeyError:
                    logging.warning(f"No mapping found for datatype {dtype} for column {column}. Letting PyArrow handle it.")
                    continue  # If mapping is not found, let PyArrow handle it

            # Use DataFrame's to_sql to insert the data into the database
            df.to_sql(target_table_name, engine, if_exists='append', index=False, dtype=dtype_mapping)

        except Exception as e:
            logging.error(f"An error occurred: {e}")


    def get_total_records(self, table_name):
        with self.connection.cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(query)
            total_records = cursor.fetchone()[0]
        return total_records

