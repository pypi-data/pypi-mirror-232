from plugin import MySQLPlugin

destination = MySQLPlugin(host='localhost', port=3306, user='root', password='my-secret-pw', dbname='your_db_name')

destination.connect()