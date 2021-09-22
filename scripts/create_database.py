import sqlite3


def create_tables(db_file="./local.persistent/event/event_store.db"):
    connect = sqlite3.connect(db_file)
    cursor = connect.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS event (id text, root_id text, type text, timestamp text, payload text)''')
    connect.commit()
    connect.close()


create_tables()
