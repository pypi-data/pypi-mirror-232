import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

class ETLController:
    def __init__(self, source_plugin, dest_plugin):
        self.source = source_plugin
        self.destination = dest_plugin

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
    def _process_batch(self, data_chunk, dest_table):
        self.destination.plugin_writer(data_chunk, dest_table)

    def dynamic_batch_generator(self, source_table, batch_size, offset=0):
        while True:
            data_chunk = next(self.source.plugin_reader(source_table, batch_size, offset), None)

            if not data_chunk:
                break

            yield data_chunk
            offset += len(data_chunk)

            if len(data_chunk) < batch_size:
                break

    def _handle_successful_batch(self, data_chunk, increase_factor, roof_batch_size):
        should_increase_batch_size = len(data_chunk) == self.current_batch_size
        if should_increase_batch_size:
            self.current_batch_size = min(int(self.current_batch_size * increase_factor), roof_batch_size)
        return should_increase_batch_size

    def _handle_failed_batch(self, data_chunk):
        self.current_batch_size = self.last_successful_batch_size
        for mini_chunk in self._divide_into_chunks(data_chunk, self.current_batch_size):
            self._process_batch(mini_chunk, self.dest_table)
        self.use_stable_batch_size = True

    def _process_data_chunks(self, generator, increase_factor, roof_batch_size):
        for data_chunk in generator:
            try:
                self._process_batch(data_chunk, self.dest_table)
                self.pbar.update(len(data_chunk))
                self.offset += len(data_chunk)
                self.last_successful_batch_size = len(data_chunk)

                if self._handle_successful_batch(data_chunk, increase_factor, roof_batch_size):
                    return True
            except Exception as e:
                logging.error(f"Error processing batch: {e}")
                self._handle_failed_batch(data_chunk)
                return False
        return False

    def execute(self, source_table, dest_table, initial_batch_size=50000, increase_factor=1.5, roof_batch_size=None):
        self.source.connect()
        self.destination.connect()

        total_records = self.source.get_total_records(table_name=source_table)
        if not roof_batch_size:
            roof_batch_size = total_records

        self.last_successful_batch_size = initial_batch_size
        self.current_batch_size = initial_batch_size
        self.offset = 0
        self.dest_table = dest_table
        self.use_stable_batch_size = False

        with tqdm(total=total_records, desc="Processing", unit="rec") as self.pbar:
            while self.current_batch_size <= roof_batch_size:
                generator = self.dynamic_batch_generator(source_table, self.current_batch_size, self.offset)

                should_increase_batch_size = self._process_data_chunks(generator, increase_factor, roof_batch_size)

                if not should_increase_batch_size:
                    break

        self.source.disconnect()
        self.destination.close_connection()

    def _divide_into_chunks(self, data, chunk_size):
        """Utility function to divide a batch of data into smaller chunks."""
        for i in range(0, len(data), chunk_size):
            yield data[i:i+chunk_size]
