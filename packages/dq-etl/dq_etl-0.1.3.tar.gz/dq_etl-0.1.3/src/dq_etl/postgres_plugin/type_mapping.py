# postgres_to_pyarrow_mapping.py

POSTGRES_TO_PYARROW_MAP = {
    'bigint': 'int64',
    'bigserial': 'int64',
    'bit': 'binary',  # or 'fixed_size_binary[n]' where n is bit length
    'bit varying': 'binary',
    'boolean': 'bool',
    'box': 'string',  # Considered as special geometric type, default to string for simplicity
    'bytea': 'binary',
    'character': 'string',
    'character varying': 'string',
    'cidr': 'string',
    'circle': 'string',  # Geometric type, default to string
    'date': 'date32',
    'double precision': 'float64',
    'inet': 'string',
    'integer': 'int32',
    'interval': 'duration[ms]',
    'json': 'string',  # Can be processed for structured data but represented as string by default
    'jsonb': 'string',
    'line': 'string',
    'lseg': 'string',
    'macaddr': 'string',
    'macaddr8': 'string',
    'money': 'decimal128',
    'numeric': 'decimal128',
    'path': 'string',
    'pg_lsn': 'string',
    'pg_snapshot': 'string',
    'point': 'string',
    'polygon': 'string',
    'real': 'float32',
    'smallint': 'int16',
    'smallserial': 'int16',
    'serial': 'int32',
    'text': 'string',
    'time': 'time32[s]',
    'time with time zone': 'time64[us]',
    'timestamp': 'timestamp[ms]',
    'timestamp with time zone': 'timestamp[ms]',  # Note: timezone information will be lost
    'tsquery': 'string',
    'tsvector': 'string',
    'txid_snapshot': 'string',
    'uuid': 'string',
    'xml': 'string'
}


PYARROW_TO_POSTGRES_MAP = {
    'int64': 'bigint',
    'binary': 'bytea',
    'bool': 'boolean',
    'string': 'text', 
    'object': 'text',  # Adding this line
    'date32': 'date',
    'float64': 'double precision',
    'int32': 'integer',
    'duration[ms]': 'interval',
    'decimal128': 'numeric',  
    'float32': 'real',
    'int16': 'smallint',
    'time32[s]': 'time',
    'time64[us]': 'time with time zone',
    'timestamp[ms]': 'timestamp',
    'fixed_size_binary': 'bit',
    'timestamp[us]': 'timestamp with time zone'
}
