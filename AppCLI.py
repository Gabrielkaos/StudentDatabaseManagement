import sqlite3

TABLE_NAME = "student_table"

def delete_data(conn):
    cursor = conn.cursor()
    student_no = input("\nDelete by Student number:")
    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE student_no = ?", (student_no,))
    data1 = cursor.fetchall()
    if len(data1) > 0:
        student = data1[0]
        print(f"\nStudent no:{student[4]}, {student[1]}, {student[2]}, {student[3][0].upper()}")
        if input(f"Are you sure you want to delete[y/n]?").lower() == "y":
            cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE student_no = ?", (student[4],))
            print("Successfully deleted!\n")
        else:print("Deleting cancelled!\n")
    else:print("No student number found!\n")
    conn.commit()

def search_student(conn):
    cursor = conn.cursor()
    search_param = input("\nSearch>").upper()

    command = f"""SELECT * 
                    FROM {TABLE_NAME} 
                    WHERE CAST(id AS TEXT) LIKE ? OR last_name LIKE ? OR first_name LIKE ? OR middle_name LIKE ? OR
                    student_no LIKE ? OR CAST(year as TEXT) LIKE ? OR course LIKE ?;"""

    cursor.execute(command,
                   (f'{search_param}%',f'{search_param}%',f'{search_param}%',f'{search_param}%',
                    f'{search_param}%',f'{search_param}%',f'{search_param}%'))
    rows = cursor.fetchall()
    conn.commit()

    #search again to double check
    space = "_"
    iteration = 0
    new_row = []
    while len(new_row)==0:
        cursor.execute(command, tuple((f'{space}{search_param}' for _ in range(7))))
        new_row = cursor.fetchall()
        space+="_"
        conn.commit()
        iteration+=1
        if iteration > 50:break
    rows.extend(new_row)
    pretty_print(rows)
    conn.commit()

def student_no_exists(conn, student_no):
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE student_no = ?", (student_no,))
    rows = cursor.fetchall()
    conn.commit()
    if len(rows) != 0: return True
    return False

def update_data(conn):
    student_no = input("\nEnter student number to edit:")

    if not student_no_exists(conn, student_no):
        print("\nStudent number doesn't exist\n")
        return
    cursor = conn.cursor()

    print("\n1.)Edit info of name\n2.)Edit year and course\n3.)Cancel editing")

    while True:
        option = input(">")
        if option == "1":
            last_name = input("Enter new last name:").upper()
            first_name = input("Enter new first name:").upper()
            middle_name = input("Enter new middle name:").upper()
            cursor.execute(
                f"UPDATE {TABLE_NAME} SET last_name = ?, first_name = ?, middle_name = ? WHERE student_no = ?",
                (last_name, first_name, middle_name, student_no))
            conn.commit()
            break
        elif option == "2":
            year = int(input("Enter new year:"))
            course = input("Enter new course:").upper()
            cursor.execute(
                f"UPDATE {TABLE_NAME} SET year = ?, course = ? WHERE student_no = ?",
                (year, course, student_no))
            conn.commit()
            break
        elif option == "3":
            print("Editing canceled!\n")
            return
        else:
            print("Select only in the 3 option!")
    print("Updated successfully\n")

def add_student(conn):
    print("\nFill out info of student")

    student_no = input("Enter Student Number:")
    if student_no_exists(conn,student_no):
        print("\nData already exists\n")
        return
    last_name = input("Enter Last Name:").upper()
    first_name = input("Enter First Name:").upper()
    middle_name = input("Enter Middle Name:").upper()
    year = int(input("Enter Year:"))
    course = input("Enter Course:").upper()
    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO {TABLE_NAME} (last_name, first_name, middle_name, student_no, year, course) VALUES (?, ?, ?, ?, ?, ?)",
        (last_name, first_name, middle_name, student_no, year, course))
    conn.commit()
    print("Student added successfully\n")

def pretty_print(rows):
    if len(rows) == 0:
        print("\nNO DATA FOUND!\n")
        return
    stars = "---+-----------------+------------------+-------------------+-------------+-----------"
    print("\nid |lastName         |firstName         |middleName         |StudentNo    |Year-Course")
    print(stars)
    for row in rows:
        end_id = "  |" if len(str(row[0])) == 1 else " |"
        print(row[0], end=end_id)

        last_name_len = len(row[1])
        print(row[1], end=f"{' ' * (17 - last_name_len)}|")

        first_name_len = len(row[2])
        print(row[2], end=f"{' ' * (18 - first_name_len)}|")

        mid_name_len = len(row[3])
        print(row[3], end=f"{' ' * (19 - mid_name_len)}|")

        student_no_name_len = len(row[4])
        print(row[4], end=f"{' ' * (13 - student_no_name_len)}|")

        print(str(row[5]) + "-" + row[6])
        print(stars)

def show_data(conn):
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()

    if len(rows) > 0:pretty_print(rows)
    else:print("No students found!\n")

    conn.commit()

def pretty_menu():
    print("\n+-------------------------------------+")
    print("| STUDENT DATABASE MANAGEMENT SYSTEM  |")
    print("+-------------------------------------+")
    print(
        f"| 1.)Add student{'|':>23}\n| 2.)Edit info{'|':>25}\n| 3.)Search student{'|':>20}\n| 4.)Show all students{'|':>17}\n| 5.)Delete data{'|':>23}\n| 6.)Exit{'|':>30}")
    print("+-------------------------------------+")

def main():
    conn = sqlite3.connect("student_database.db")

    cursor = conn.cursor()

    cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY,
                last_name TEXT,
                first_name TEXT,
                middle_name TEXT,
                student_no TEXT,
                year INTEGER,
                course TEXT
            )
        """)

    conn.commit()

    func_dict = {1: add_student, 2: update_data, 5: delete_data, 4: show_data, 3: search_student}

    while True:
        try:
            pretty_menu()
            inputs = int(input("Select option>"))
            if inputs==6:break
            func_dict[inputs](conn)
        except ValueError:
            print("\nWrong Input\n")
        except KeyError:
            print("\nWrong Input\n")

    conn.commit()
    conn.close()


if __name__=="__main__":
    main()