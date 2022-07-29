import getopt
import sqlite3
import sys


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "f:", ["file="])
        opt, arg = opts[0]
        if opt in ("-f", "--file"):
            create_tables(arg)
    except getopt.GetoptError:
        create_tables()
    except IndexError:
        create_tables()


def create_tables(db_file="./local.persistent/event/event_store.db"):
    connect = sqlite3.connect(db_file)
    cursor = connect.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS event (id text, root_id text, type text, timestamp text, payload text)"""
    )
    connect.commit()
    connect.close()


if __name__ == "__main__":
    main(sys.argv[1:])
