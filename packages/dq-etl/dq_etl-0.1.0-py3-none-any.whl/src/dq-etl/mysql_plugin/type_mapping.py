# pyarrow_to_mysql_mapping.py

PYARROW_TO_MYSQL_MAP = {
    'int8': 'TINYINT',
    'int16': 'SMALLINT',
    'int32': 'INT',
    'int64': 'BIGINT',
    'uint8': 'TINYINT UNSIGNED',
    'uint16': 'SMALLINT UNSIGNED',
    'uint32': 'INT UNSIGNED',
    'uint64': 'BIGINT UNSIGNED',
    'float16': 'FLOAT',  # Note: MySQL does not have a true half-precision float.
    'float32': 'FLOAT',
    'float64': 'DOUBLE',
    'bool': 'BOOLEAN',
    'object': 'VARCHAR(255)',  # Strings
    'O': 'TEXT',  # Larger strings or mixed types
    'datetime64[ns]': 'DATETIME(6)',  # Maximum MySQL precision is microseconds.
    'datetime64[ms]': 'DATETIME(3)',
    'date': 'DATE',
    'timedelta64[ns]': 'BIGINT',  # Duration in nanoseconds. Consider using BIGINT
    # Add more types as needed...
}
MYSQL_TO_PYARROW_MAP = {
    'TINYINT': 'int8',
    'SMALLINT': 'int16',
    'INT': 'int32',
    'MEDIUMINT': 'int32',
    'BIGINT': 'int64',
    'TINYINT UNSIGNED': 'uint8',
    'SMALLINT UNSIGNED': 'uint16',
    'INT UNSIGNED': 'uint32',
    'MEDIUMINT UNSIGNED': 'uint32',
    'BIGINT UNSIGNED': 'uint64',
    'FLOAT': 'float32',
    'DOUBLE': 'float64',
    'DECIMAL': 'decimal128', 
    'BOOLEAN': 'bool',
    'CHAR': 'string',
    'VARCHAR': 'string',
    'TEXT': 'string',
    'MEDIUMTEXT': 'string',
    'LONGTEXT': 'string',
    'DATE': 'date32',
    'DATETIME': 'timestamp[us]',
    'TIMESTAMP': 'timestamp[us]',
    'TIME': 'time64[us]',
    'YEAR': 'int16',
    'BINARY': 'binary',
    'VARBINARY': 'binary',
    'TINYBLOB': 'binary',
    'MEDIUMBLOB': 'binary',
    'BLOB': 'binary',
    'LONGBLOB': 'binary',
    'ENUM': 'string',
    'SET': 'string',
}
