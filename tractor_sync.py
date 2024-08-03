"""Tractor Sync
    By Michael Fulcher

    Send Donations (recommended $1.50USD) to -
    PayPal: mjfulcher58@gmail.com
    Bitcoin: 3DXiJxie6En3wcyxjmKZeY2zFLEmK8y42U
    Other options @ http://michaelfulcher.yolasite.com/
"""
# code
import sys
import os
import shutil
import sqlite3
import pathlib
from platform import node
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

CURRENT_DATABASE_VERSION = '1.1.2'
RELATIVE_DB_PATH = r'.\data\tractorsync.db'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, RELATIVE_DB_PATH)
CURRENT_NODE = node()

# Functions to handle CRUD operations
def is_valid_path(a_path, feedback=True) -> tuple:
    """
    Helper to confirm if the folder path provided is one that exists at that time.
    :param feedback:
    :param a_path:
    :return:
    """
    if os.path.exists(a_path) or pathlib.Path(a_path).exists():
        if feedback:
            print(f"The path {a_path} exists.")
        if a_path.find("\\\\") != -1:
            return True, "N"
        return True, "L"
    if feedback:
        print(f"The path {a_path} does not exist.")
    return False, "E"

def get_file_names(source) -> list:
    """
    Gets the names of all files in a folder and returns a list of filenames.
    :param source:
    :return:
    """
    file_list = []
    try:
        for file in os.listdir(source):
            if os.path.isfile(os.path.join(source, file)):
                file_list.append(file)
    except NotADirectoryError as e:
        print(f"Failed as provided {source} is not a directory. Reason: {str(e)}")
    except Exception as e:
        print(f"Failed to list files in directory. Reason: {str(e)}")
    return file_list

def file_list_insert_db_transactions(db_cursor, sync_id, file_list):
    """
    For use by an open sqlite3 connection generates and submits the transaction for a file linked to SyncFeedInfo_id
    :param db_cursor:
    :param sync_id:
    :param file_list:
    :return n:
    """
    n = 0
    for file in file_list:
        try:
            db_cursor.execute("INSERT INTO folderContent (syncFeedInfo_id, fileName, listOrder) VALUES (?, ?, ?);", (sync_id, file, n))
            n += 1
        except Exception as e:
            print("Failed to update the database for file {}. Reason: {}".format(file, e))
    return n

def update_entry_destination(db_id) -> None:
    """
    Does the entire data update process for a new destination folder.
    :param db_id:
    :return:
    """
    is_input_valid = False
    while not is_input_valid:
        destination_folder = input("Enter destination folder: ")
        is_input_valid, dest_path_type = is_valid_path(destination_folder)
    with closing(sqlite3.connect(DB_PATH)) as db_connection:
        with closing(db_connection.cursor()) as cur:
            cur.execute("UPDATE syncFeedInfo SET destinationFolder = ?, destinationPathType = ? WHERE id = ?;", (destination_folder, dest_path_type, db_id))
            db_connection.commit()

def create_new_entry() -> None:
    """
    Does the entire data collection process for a new folder."
    :return: 
    """""
    is_input_valid = False
    while not is_input_valid:
        source = input("Enter source folder: ")
        is_input_valid, source_path_type = is_valid_path(source)
    is_input_valid = False
    while not is_input_valid:
        destination = input("Enter destination folder: ")
        is_input_valid, dest_path_type = is_valid_path(destination)
    file_list = get_file_names(source)
    if len(file_list) == 0:
        print("No files found. - New entry will not be made.")
        return
    try:
        with closing(sqlite3.connect(DB_PATH)) as db_connection:
            with closing(db_connection.cursor()) as cur:
                cur.execute("INSERT INTO syncFeedInfo (sourceFolder, sourcePathType, destinationFolder, destinationPathType, pcName) VALUES (?, ?, ?, ?, ?);", (source, source_path_type, destination, dest_path_type, CURRENT_NODE))
                db_id = cur.execute("SELECT id FROM syncFeedInfo ORDER BY id DESC LIMIT 1;").fetchone()[0]
                length = file_list_insert_db_transactions(cur, db_id, file_list)
                db_connection.commit()
    except Exception as e:
        print("Failed to update the database. Reason: ", e)
    finally:
        print(f'Sync data created Source: {source} Destination: {destination} and {length} Files found.')

def update_entry_source(db_id) -> None:
    """
    Now does the entire data update process for a new source folder.
    :param db_id:
    :return:
    """
    is_input_valid = False
    while not is_input_valid:
        source_folder = input("Enter source folder: ")
        is_input_valid, source_path_type = is_valid_path(source_folder)
    with closing(sqlite3.connect(DB_PATH)) as db_connection:
        with closing(db_connection.cursor()) as cur:
            cur.execute("SELECT sourceFolder FROM syncFeedInfo WHERE id = ?;", (db_id,))
            old_source_folder = cur.fetchone()[0]
    if old_source_folder != source_folder:
        file_search_answer = input("This will remove the file information.\nDo you want to continue? [Y/N] ")
        if file_search_answer.lower() == 'y':
            with closing(sqlite3.connect(DB_PATH)) as db_connection:
                with closing(db_connection.cursor()) as cur:
                    cur.execute("DELETE FROM folderContent WHERE syncFeedInfo_id = ?;", (db_id,))
                    file_list = get_file_names(source_folder)
                    if len(file_list) == 0:
                        print("No files found.")
                        return
                    length = file_list_insert_db_transactions(cur, db_id, file_list)
                    cur.execute("UPDATE syncFeedInfo SET sourceFolder = ?, sourcePathType = ? WHERE id = ?;", (source_folder, source_path_type, db_id))
                    db_connection.commit()
                    print(f"Source folder was updated, with {length} file(s) added.")
    else:
        print("New source folder is the same as the old one. No changes were made.")

def read_entries():
    with closing(sqlite3.connect(DB_PATH)) as db_connection:
        with closing(db_connection.cursor()) as cur:
            cur.execute("SELECT * FROM syncFeedInfo")
            for row in cur.fetchall():
                print(row)

def delete_entry(db_id) -> None:
    with closing(sqlite3.connect(DB_PATH)) as db_connection:
        with closing(db_connection.cursor()) as cur:
            cur.execute("DELETE FROM syncFeedInfo WHERE id = ?;", (db_id,))
            cur.execute("DELETE FROM folderContent WHERE syncFeedInfo_id = ?;", (db_id,))
            db_connection.commit()

def change_status(db_id, status) -> None:
    try:
        with closing(sqlite3.connect(DB_PATH)) as db_connection:
            with closing(db_connection.cursor()) as cur:
                cur.execute("UPDATE syncFeedInfo SET enabled = ? WHERE id = ?;", (status, db_id))
                db_connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def enable_disable_files(db_id, file_state, file_name):
    try:
        with closing(sqlite3.connect(DB_PATH)) as db_connection:
            with closing(db_connection.cursor()) as cur:
                cur.execute("UPDATE foldercontent SET enabled = ? WHERE syncFeedInfo_id = ? AND fileName = ?;", (file_state, db_id, file_name))
                db_connection.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def enable_disable_files_by_extension(db_id, file_extension, file_state):
    try:
        with closing(sqlite3.connect(DB_PATH)) as db_connection:
            with closing(db_connection.cursor()) as cur:
                cur.execute("UPDATE folderContent SET enabled = ? WHERE syncFeedInfo_id = ? AND fileName LIKE '%' || ? || '';", (file_state, db_id, file_extension))
                db_connection.commit()
    except sqlite3.Error as e:
            print(f"An error occurred: {e}")

def advance_current_entry(curr_id) -> None:
    """
    Advances the current file by 1 in the entry with the given id.
    :param curr_id: The id of the entry to advance the current file.
    :return: None
    """
    try:
        with closing(sqlite3.connect(DB_PATH)) as db_connection:
            with closing(db_connection.cursor()) as cur:
                cur.execute("SELECT current_id FROM syncFeedInfo WHERE id = ?;", (curr_id,))
                current_id = cur.fetchone()[0]
                cur.execute("UPDATE syncFeedInfo SET current_id = ? WHERE id = ?;", (current_id + 1, curr_id))
                db_connection.commit()
    except ValueError:
        print("Invalid ID! Try Again...")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def edit_file_state(db_id) -> None:
    while True:
        with closing(sqlite3.connect(DB_PATH)) as db_connection:
            with closing(db_connection.cursor()) as cur:
                results = cur.execute("SELECT * FROM folderContent WHERE syncFeedInfo_id = ?;", (db_id,))
                for row in results:
                    print(row)
        print("1. Enable/disable by name files")
        print("2. Enable/disable files by extension")
        print("Q. Go back")
        option = input("Select an option: ")

        if option == '1':
            file_extension = input("Enter file name: ")
            state = int(input("Enter state (1 - Enabled, 0 - Disabled): "))
            enable_disable_files(db_id, state, file_extension)
        elif option == '2':
            file_extension = input("Enter file extension: ")
            state = int(input("Enter state (1 - Enabled, 0 - Disabled): "))
            enable_disable_files_by_extension(db_id, file_extension, state)
        elif option.lower() == 'q':
            break
        else:
            print("Invalid option, please try again.")

def edit_menu() -> None:
    while True:
        print("1. Update source folder")
        print("2. Update destination folder")
        print("3. Delete entry")
        print("4. Enable/disable files")
        print("S. Setting")
        print("Q. Go back")
        option = input("Select an option: ")
        try:
            if option == '1':
                curr_id = int(input("Enter id of the entry to update: "))
                update_entry_source(curr_id)
            elif option == '2':
                curr_id = int(input("Enter id of the entry to update: "))
                update_entry_destination(curr_id)
            elif option == '3':
                curr_id = int(input("Enter id of the entry to delete: "))
                delete_entry(curr_id)
            elif option == '4':
                curr_id = int(input("Enter id of the source folder to edit: "))
                edit_file_state(curr_id)
            option = option.lower()
            if option == 's':
                print('setting not implemented')
                ## toggle logging
            elif option == 'q':
                break
            else:
                print("Invalid option, please try again.")
        except ValueError:
            print("Invalid option, please try again.")


def main() -> None:
    while True:
        read_entries()
        print("1. Create new entry")
        print("2. Edit entries")
        print("3. Enable entry")
        print("4. Disable entry")
        print("5. Advance Current File by n")
        print("Q. Quit")
        option = input("Select an option: ")

        if option == '1':
            create_new_entry()
        elif option == '2':
            edit_menu()
        elif option == '3':
            try:
                curr_id = int(input("Enter id of the entry to enable: "))
                change_status(curr_id, 1)
            except ValueError:
                print("Invalid ID! Try Again...")
        elif option == '4':
            try:
                curr_id = int(input("Enter id of the entry to disable: "))
                change_status(curr_id, 0)
            except ValueError:
                print("Invalid ID! Try Again...")
        elif option == '5':
            try:
                curr_id = int(input("Enter id of the entry to advance the current file: "))
                advance_current_entry(curr_id)
            except ValueError:
                print("Invalid ID! Try Again...")
        elif option.lower() == 'q':
            break
        else:
            print("Invalid option, please try again.")

def perform_past_file_check_and_delete(cur, dest_file, list_pos, list_id) -> None:
    if list_pos > 0:
        result2 = cur.execute("SELECT fileName FROM folderContent WHERE syncFeedInfo_id = ? AND listOrder = ?", (list_id, list_pos - 1)).fetchone()
        if result2 is not None:
            previous_file = os.path.join(dest_file[:dest_file.rfind('\\')], result2[0])
            if os.path.isfile(previous_file):
                os.remove(previous_file)
                print(f'Deleted {previous_file}')

def perform_file_check_and_move(cur, src_file: str, dest_file: str, list_pos, list_id) -> None:
    if not os.path.isfile(dest_file):
        try:
            shutil.copy(src_file, dest_file)
            print(f'Copied {src_file} to {dest_file}')
            perform_past_file_check_and_delete(cur, dest_file, list_pos, list_id)
        except FileNotFoundError:
            print(f'Could not copy {src_file} to {dest_file}. {src_file} not found')
    else:
        perform_past_file_check_and_delete(cur, dest_file, list_pos, list_id)

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "/m":
            if not os.path.isdir(r'.\data'):
                os.mkdir(r'.\data')
            if not os.path.isfile(DB_PATH):
                # Establish a connection to the database
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS syncFeedInfo (
                        id INTEGER PRIMARY KEY,
                        sourceFolder TEXT NOT NULL,
                        sourcePathType CHAR(1) NOT NULL,
                        destinationFolder TEXT NOT NULL,
                        destinationPathType CHAR(1) NOT NULL,
                        current_id INTEGER NOT NULL DEFAULT 0,
                        dateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
                        pcName TEXT,
                        enabled INTEGER DEFAULT 1
                    );''')

                    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS folderContent (
                        syncFeedInfo_id INTEGER,
                        fileName TEXT NOT NULL,
                        listOrder INTEGER,
                        statusCode CHAR(1) DEFAULT "A",
                        enabled INTEGER DEFAULT 1,
                        PRIMARY KEY (fileName, syncFeedInfo_id),
                        FOREIGN KEY(syncFeedInfo_id) REFERENCES syncFeedInfo(id)
                    );''')

                    cursor.execute("""
                    CREATE TABLE IF NOT EXISTS version (
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP PRIMARY KEY, 
                        major INTEGER NOT NULL, minor INTEGER NOT NULL, patch INTEGER NOT NULL 
                    );""")

                    cursor.execute("INSERT INTO version(major, minor, patch) VALUES (?, ?, ?);", ([int(x) for x in CURRENT_DATABASE_VERSION.split('.')]))

                    conn.commit()
                    print('Created Database')
            else:
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM version ORDER BY timestamp DESC LIMIT 1;")
                    result = cursor.fetchone()
                    if result is None:
                        cursor.execute("ALTER TABLE version RENAME COLUMN minor TO patch;")
                        cursor.execute("ALTER TABLE version RENAME COLUMN major TO minor;")
                        cursor.execute("ALTER TABLE version RENAME COLUMN version TO major;")
                        version_list = (1, 0, 2)
                        cursor.execute("INSERT INTO version(major, minor, patch) VALUES (?, ?, ?)", version_list)
                        print(f'Database upgraded to version {'.'.join(str(x) for x in version_list)}')
                        conn.commit()
                    else:
                        version_list = list(result)
                    if '.'.join(str(x) for x in version_list[1:]) != CURRENT_DATABASE_VERSION:
                        if version_list[1] == 1:
                            if version_list[2] == 0:
                                cursor.execute("PRAGMA foreign_keys=off;")
                                cursor.execute("ALTER TABLE filenames RENAME TO old_filenames;")
                                cursor.execute('''
                                CREATE TABLE IF NOT EXISTS folderContent (
                                    syncFeedInfo_id INTEGER,
                                    fileName TEXT NOT NULL,
                                    listOrder INTEGER,
                                    statusCode CHAR(1) DEFAULT "A",
                                    enabled INTEGER DEFAULT 1,
                                    PRIMARY KEY (fileName, syncFeedInfo_id),
                                    FOREIGN KEY(syncFeedInfo_id) REFERENCES syncFeedInfo(id)
                                );''')
                                cursor.execute("INSERT INTO folderContent(syncFeedInfo_id, fileName, listOrder, statusCode, enabled) SELECT syncFeedInfo_id, fileName, listOrder, statusCode, enabled FROM old_filenames;")
                                cursor.execute("DROP TABLE old_filenames;")
                                cursor.execute("ALTER TABLE syncFeedInfo RENAME TO syncFeedInfo_old;")
                                cursor.execute('''CREATE TABLE IF NOT EXISTS syncFeedInfo (
                                                        id INTEGER PRIMARY KEY,
                                                        sourceFolder TEXT NOT NULL,
                                                        sourcePathType CHAR(1) NOT NULL,
                                                        destinationFolder TEXT NOT NULL,
                                                        destinationPathType CHAR(1) NOT NULL,
                                                        dateCreated DATETIME DEFAULT CURRENT_TIMESTAMP,
                                                        enabled INTEGER DEFAULT 1
                                                    );''')
                                cursor.execute("INSERT INTO syncFeedInfo(id, sourceFolder, sourcePathType, destinationFolder, destinationPathType, dateCreated, enabled) SELECT id, sourceFolder, CASE WHEN sourceFolder LIKE '%\\\\%' THEN 'N' ELSE 'L' END, destinationFolder, CASE WHEN destinationFolder LIKE '%\\\\%' THEN 'N' ELSE 'L' END, dateCreated, enabled FROM syncFeedInfo_old;")
                                cursor.execute("DROP TABLE syncFeedInfo_old;")
                                cursor.execute("PRAGMA foreign_keys=on;")
                                version_list[2], version_list[3] = 1, 0
                            if version_list[3] == 0:
                                cursor.execute("ALTER TABLE syncFeedInfo ADD COLUMN pcName TEXT;")
                                version_list[3] = 1
                            if version_list[3] == 1:
                                cursor.execute("ALTER TABLE syncFeedInfo ADD COLUMN current_id INTEGER NOT NULL DEFAULT 0;")
                                version_list[3] = 2
                            cursor.execute("INSERT INTO version (major, minor, patch) VALUES (?, ?, ?)", tuple(version_list[1:]))
                            print(f'Database upgraded to version {'.'.join(str(x) for x in version_list[1:])}')
                        conn.commit()
                    else:
                        print(f"Current database version: {'.'.join(str(x) for x in version_list[1:])}")
            main()
        elif sys.argv[1] == '/s':
            if os.path.isfile(DB_PATH):
                with closing(sqlite3.connect(DB_PATH)) as conn:
                    with closing(conn.cursor()) as cursor:
                        cursor.execute("SELECT major, minor, patch FROM version ORDER BY timestamp DESC LIMIT 1;")
                        version = cursor.fetchone()
                        if '.'.join(str(x) for x in version) == CURRENT_DATABASE_VERSION:
                            print(f"Current database version: {'.'.join(str(x) for x in version)}")
                            result = cursor.execute("SELECT syncFeedInfo.sourceFolder, syncFeedInfo.destinationFolder, fileName, listOrder, syncFeedInfo_id FROM folderContent JOIN syncFeedInfo ON syncFeedInfo.id = syncFeedInfo_id WHERE syncFeedInfo.enabled = 1 AND syncfeedinfo.pcName = ? AND folderContent.listOrder = syncFeedInfo.current_id;", (CURRENT_NODE,)).fetchall()
                            print(result)
                            if len(result) == 0:
                                print("Please run the script with the /m argument to create or access the database.")
                            else:
                                network_sources_dict = {}
                                network_host_list = []
                                for line in result:
                                    source_file = os.path.join(line[0], line[2])
                                    destination_file = os.path.join(line[1], line[2])
                                    is_input_valid, path_type = is_valid_path(line[0], False)
                                    is_input_valid_des, path_type_des = is_valid_path(line[1], False)
                                    if is_input_valid and is_input_valid_des:
                                        if path_type == 'N' or path_type_des == 'N':
                                            if path_type == 'N':
                                                host_name = source_file[2:source_file[2:].find('\\') + 2]
                                            elif path_type_des == 'N':
                                                host_name = destination_file[2:destination_file[2:].find('\\') + 2]
                                            if host_name in network_host_list:
                                                network_sources_dict[host_name].append(line)
                                            else:
                                                network_host_list.append(host_name)
                                                network_sources_dict[host_name] = [line]
                                        else:
                                            perform_file_check_and_move(cursor, source_file, destination_file, line[3], line[4])
                                for host_name in network_host_list:
                                    for line in network_sources_dict[host_name]:
                                        if os.path.isdir(line[0]):
                                            source_file = os.path.join(line[0], line[2])
                                            destination_file = os.path.join(line[1], line[2])
                                            perform_file_check_and_move(cursor, source_file, destination_file, line[3], line[4])
                        else:
                            print(f"Current database out of date, run /m to update.")
            else:
                print("Please run the script with the /m argument to create or access the database.")
    else:
        print("Please run the script with the /m argument to create or access the database.")
