import sys
import os
import sqlite3
from contextlib import closing

print("'make a cube'")
print("     /|")
print("    / |")
print("   /  |")
print("  /___|")
print(" |   | |")
print(" |___|_|")

print('"use the orginal cube attempt and add a sphear"')
print("  ****")
print(" *    *")
print("*      *")
print("*      *")
print(" *    *")
print("  ****")

CURRENT_DATABASE_VERSION = '1.0.2'
DB_PATH = r'.\data\tractorsync.db'

# Functions to handle CRUD operations
def create_new_entry(source_folder, destination_folder):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO syncFeedInfo (sourceFolder, destinationFolder) VALUES (?, ?)", (source_folder, destination_folder))
        conn.commit()


def update_entry_source(db_id, source_folder):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE syncFeedInfo SET sourceFolder = ? WHERE id = ?", (source_folder, db_id))
        conn.commit()


def update_entry_destination(db_id, destination_folder):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE syncfeedinfo SET destinationFolder = ? WHERE id = ?", (destination_folder, db_id))
        conn.commit()


def read_entries():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM syncFeedInfo")
        rows = cursor.fetchall()
        for row in rows:
            print(row)


def update_entry(db_id, source_folder, destination_folder):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE syncFeedInfo S ET sourceFolder = ?, destination_folder = ? WHERE id = ?", (source_folder, destination_folder, db_id))
        conn.commit()


def delete_entry(db_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM syncFeedInfo WHERE id = ?", (db_id,))
        conn.commit()


def change_status(db_id, status):
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE syncFeedInfo SET enabled = ? WHERE id = ?", (status, db_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


def edit_menu():
    while True:
        print("1. Update source folder")
        print("2. Update destination folder")
        print("3. Delete entry")
        print("Q. Go back")
        option = input("Select an option: ")

        if option == '1':
            curr_id = int(input("Enter id of the entry to update: "))
            source = input("Enter new source folder: ")
            update_entry_source(curr_id, source)
        elif option == '2':
            curr_id = int(input("Enter id of the entry to update: "))
            destination = input("Enter new destination folder: ")
            update_entry_destination(curr_id, destination)
        elif option == '3':
            curr_id = int(input("Enter id of the entry to delete: "))
            delete_entry(curr_id)
        elif option.lower() == 'q':
            break
        else:
            print("Invalid option, please try again.")


def main():
    while True:
        read_entries()
        print("1. Create new entry")
        print("2. Edit entries")
        print("3. Enable entry")
        print("4. Disable entry")
        print("Q. Quit")
        option = input("Select an option: ")

        if option == '1':
            source = input("Enter source folder: ")
            destination = input("Enter destination folder: ")
            create_new_entry(source, destination)
        elif option == '2':
            edit_menu()
        elif option == '3':
            curr_id = int(input("Enter id of the entry to enable: "))
            change_status(curr_id, 1)
        elif option == '4':
            curr_id = int(input("Enter id of the entry to disable: "))
            change_status(curr_id, 0)
        elif option.lower() == 'q':
            break
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "/m":
            if not os.path.isdir(r'.\data'):
                os.mkdir(r'.\data')
            if not os.path.isfile(DB_PATH):
                # Establish a connection to the database
                with closing(sqlite3.connect(DB_PATH)) as conn:  # The database name
                    cursor = conn.cursor()

                    # Rename and modify the tables as per new requirements
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS syncFeedInfo (
                        id INTEGER PRIMARY KEY,
                        sourceFolder TEXT NOT NULL,
                        destinationFolder TEXT NOT NULL,
                        dateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        enabled INTEGER DEFAULT 1
                    );''')

                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS filenames (
                        id INTEGER PRIMARY KEY,
                        syncFeedInfo_id INTEGER,
                        fileName TEXT NOT NULL,
                        listOrder INTEGER,
                        statusCode CHAR(1) DEFAULT "A",
                        enabled INTEGER DEFAULT 1,
                        FOREIGN KEY(syncFeedInfo_id) REFERENCES syncFeedInfo(id)
                    );''')

                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS version (
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP PRIMARY KEY, 
                        major INTEGER NOT NULL, minor INTEGER NOT NULL, patch INTEGER NOT NULL 
                    );""")


                    cursor.execute("INSERT INTO version(major, minor, patch) VALUES (?, ?, ?)", ([int(x) for x in CURRENT_DATABASE_VERSION.split('.')]))

                    conn.commit()
                    print('Created Database')
            else:
                with closing(sqlite3.connect(DB_PATH)) as conn:  # The database name
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM version ORDER BY timestamp DESC LIMIT 1;")
                    if cursor.fetchone() is None:
                        cursor.execute("ALTER TABLE version RENAME COLUMN minor TO patch;")
                        cursor.execute("ALTER TABLE version RENAME COLUMN major TO minor;")
                        cursor.execute("ALTER TABLE version RENAME COLUMN version TO major;")
                        version_list = (1, 0, 2)
                        cursor.execute("INSERT INTO version(major, minor, patch) VALUES (?, ?, ?)", version_list)
                        print(f'Database upgraded to version {'.'.join(str(x) for x in version_list)}')
                        conn.commit()
            main()
        elif sys.argv[1] == '/s':
            if os.path.isfile(DB_PATH):
                print("Found Database, sync not implemented")
            else:
                print("Please run the script with the /m argument to create or access the database.")
    else:
        print("Please run the script with the /m argument to create or access the database.")
