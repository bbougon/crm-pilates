import sqlite3


def create_tables():
    connect = sqlite3.connect("./local.persistent/event/event_store.db")
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE event (id text, root_id text, type text, timestamp text, payload text)''')
    connect.commit()
    connect.close()


create_tables()