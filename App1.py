import sqlite3
import tkinter as tk
from tkinter import END,messagebox,ttk
import csv

root = tk.Tk()
root.title("Database Management System")
TABLE_NAME = "student_table"

def student_no_exists(conn, student_no):
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE student_no = ?", (student_no,))
    rows = cursor.fetchall()
    conn.commit()
    if len(rows) != 0: return True
    return False

def clear_tree(tree):
    tree.delete(*tree.get_children())
def search_all_gui_second(tree,search_param):

    clear_tree(tree)

    conn = sqlite3.connect("student_database.db")
    cursor = conn.cursor()

    command = f"""SELECT * 
                        FROM {TABLE_NAME} 
                        WHERE CAST(id AS TEXT) LIKE ? OR last_name LIKE ? OR first_name LIKE ? OR middle_name LIKE ? OR
                        student_no LIKE ? OR CAST(year as TEXT) LIKE ? OR course LIKE ?;"""

    cursor.execute(command,
                   (f'{search_param}%', f'{search_param}%', f'{search_param}%', f'{search_param}%',
                    f'{search_param}%', f'{search_param}%', f'{search_param}%'))
    rows = cursor.fetchall()
    conn.commit()

    # search again to double check(hack)
    space = "_"
    iteration = 0
    new_row = []
    while len(new_row) == 0:
        cursor.execute(command, tuple((f'{space}{search_param}' for _ in range(7))))
        new_row = cursor.fetchall()
        space += "_"
        conn.commit()
        iteration += 1
        if iteration > 50: break
    rows.extend(new_row)
    conn.close()

    data = []

    for row in rows:
        data1 = [str(i) for i in row]
        course = data1.pop()
        data1[-1] += f"-{course}"
        data.append(tuple(data1))

    for item in tree.get_children():
        tree.delete(item)

    for item in data:
        tree.insert("", tk.END, values=item)
def delete_gui(tree):
    conn = sqlite3.connect("student_database.db")

    try:
        student_no = tree.item(tree.focus(), "values")[-2]
    except IndexError:
        student_no = ""

    cursor = conn.cursor()
    if student_no != "" and student_no_exists(conn,student_no):
        tree.delete(*tree.get_children())
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE student_no = ?", (student_no,))
        data1 = cursor.fetchall()
        if len(data1) > 0:
            student = data1[0]
            if messagebox.askyesno("Confirmation", f"\nStudent no:{student[4]}, {student[1]}, {student[2]}, {student[3][0].upper()}\nAre you sure you want to delete?"):
                cursor.execute(f"DELETE FROM {TABLE_NAME} WHERE student_no = ?", (student[4],))
                show_success("Successfully deleted!\n")
            else:
                show_error("Deleting cancelled!\n")
        else:
            show_error("No student number found!\n")
        conn.commit()
    else:
        conn.commit()
    conn.close()

def gui_edit_third(last_name,first_name,mid_name,year,course,student_no,window1):
    last_txt = str(last_name.get("1.0",END).rstrip())
    first_txt = str(first_name.get("1.0", END).rstrip())
    mid_txt = str(mid_name.get("1.0",END).rstrip())
    year_txt = int(year.get("1.0", END).rstrip())
    course_txt = str(course.get("1.0",END).rstrip())

    conn = sqlite3.connect("student_database.db")

    cursor = conn.cursor()

    cursor.execute(
        f"UPDATE {TABLE_NAME} SET last_name = ?, first_name = ?, middle_name = ?, year = ?, course = ? WHERE student_no = ?",
        (last_txt, first_txt, mid_txt,year_txt,course_txt, student_no))
    conn.commit()
    conn.close()
    show_success("Updated successfully!")
    window1.destroy()
def gui_edit_second(tree):
    second_window = tk.Toplevel(root)
    second_window.title("Edit info")
    second_window.geometry("400x500")


    conn = sqlite3.connect("student_database.db")

    try:
        student_no = tree.item(tree.focus(),"values")[-2]
    except IndexError:
        student_no = ""

    tree.delete(*tree.get_children())

    if student_no_exists(conn,student_no):
        cursor = conn.execute(f"SELECT * FROM {TABLE_NAME} WHERE student_no = ? ",(student_no,))

        rows = cursor.fetchall()
        conn.commit()

        last_txt = rows[0][1]
        first_txt = rows[0][2]
        mid_txt = rows[0][3]
        year_txt = rows[0][5]
        course_txt = rows[0][6]

        last_name_label = tk.Label(second_window, text="Enter new Last Name")
        last_name_label.pack(pady=10)
        last_name = tk.Text(second_window, width=20, height=1)
        last_name.insert("1.0",last_txt)
        last_name.pack()

        first_name_label = tk.Label(second_window, text="Enter new First Name")
        first_name_label.pack()
        first_name = tk.Text(second_window, width=20, height=1)
        first_name.insert("1.0", first_txt)
        first_name.pack()

        mid_name_label = tk.Label(second_window, text="Enter new Middle Name")
        mid_name_label.pack()
        mid_name = tk.Text(second_window, width=20, height=1)
        mid_name.insert("1.0",mid_txt)
        mid_name.pack()

        year_label = tk.Label(second_window, text="Enter new Year")
        year_label.pack()
        year = tk.Text(second_window, width=20, height=1)
        year.insert("1.0",year_txt)
        year.pack()

        course_label = tk.Label(second_window, text=f"Enter new Course")
        course_label.pack()
        course = tk.Text(second_window, width=20, height=1)
        course.insert("1.0",course_txt)
        course.pack()

        edit_student_btn = tk.Button(second_window, text="Save edited info", font=("Arial", 18),command=lambda : gui_edit_third(last_name,first_name,mid_name,year,course,student_no,second_window))
        edit_student_btn.pack(pady=100)
        conn.close()

        second_window.mainloop()
    else:
        second_window.destroy()
        show_error("No student found/selected")
        conn.commit()
        conn.close()
        return

def show_success(text):
    messagebox.showinfo("Success",text)
def show_error(text):
    messagebox.showinfo("Error",text)

def gui_add_first():

    second_window = tk.Toplevel(root)
    second_window.geometry("400x500")
    second_window.title("Add student")

    last_name_label = tk.Label(second_window,text="Last Name",font=("Arial",10))
    last_name_label.pack()
    last_name = tk.Text(second_window,width=20,height=1,font=("Arial",18))
    last_name.pack()

    first_name_label = tk.Label(second_window, text="First Name",font=("Arial",10))
    first_name_label.pack()
    first_name = tk.Text(second_window,width=20, height=1,font=("Arial",18))
    first_name.pack()

    mid_name_label = tk.Label(second_window, text="Middle Name",font=("Arial",10))
    mid_name_label.pack()
    mid_name = tk.Text(second_window,width=20, height=1,font=("Arial",18))
    mid_name.pack()

    student_no_label = tk.Label(second_window, text="Student Number",font=("Arial",10))
    student_no_label.pack()
    student_no = tk.Text(second_window,width=20, height=1,font=("Arial",18))
    student_no.pack()

    year_label = tk.Label(second_window, text="Year",font=("Arial",10))
    year_label.pack()
    year = tk.Text(second_window,width=20, height=1,font=("Arial",18))
    year.pack()

    course_label = tk.Label(second_window, text="Course",font=("Arial",10))
    course_label.pack()
    course = tk.Text(second_window, width=20, height=1,font=("Arial",18))
    course.pack()

    add_student_btn = tk.Button(second_window,text="Add student",font=("Arial",18),command=lambda:gui_add_second(second_window,last_name,first_name,mid_name,student_no,year,course))
    add_student_btn.pack(pady=10)

    second_window.mainloop()
def gui_add_second(win,last_name,first_name,mid_name,student_no,year,course):
    last = str(last_name.get("1.0",END).rstrip()).upper()
    first = str(first_name.get("1.0",END).rstrip()).upper()
    mid = str(mid_name.get("1.0", END).rstrip()).upper()
    student_n = str(student_no.get("1.0", END).rstrip())
    yr = int(year.get("1.0",END).rstrip())
    course1 = str(course.get("1.0",END).rstrip()).upper()

    conn1 = sqlite3.connect("student_database.db")
    if student_no_exists(conn1,student_n):
        show_error("Student number already exists")
        clear_field_add(last_name,first_name,mid_name,student_no,year,course)
        win.destroy()
        conn1.close()
        return
    conn1.close()

    conn = sqlite3.connect("student_database.db")

    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO {TABLE_NAME} (last_name, first_name, middle_name, student_no, year, course) VALUES (?, ?, ?, ?, ?, ?)",
        (last, first, mid, student_n, yr, course1))

    clear_field_add(last_name,first_name,mid_name,student_no,year,course)
    show_success("Student added!")
    win.destroy()
    conn.commit()
    conn.close()
def clear_field_add(last_name,first_name,mid_name,student_no,year,course):
    last_name.delete("1.0",END)
    first_name.delete("1.0",END)
    mid_name.delete("1.0",END)
    student_no.delete("1.0",END)
    year.delete("1.0",END)
    course.delete("1.0",END)

def insert_student(conn,last_name,first_name,middle_name,student_no,course,year):
    cursor = conn.cursor()


    cursor.execute(f"INSERT INTO {TABLE_NAME} (last_name, first_name, middle_name, student_no, course, year) VALUES (?, ?, ?, ?, ?, ?)",
                   (last_name,first_name,middle_name,student_no,course,year))

    conn.commit()

def add_file_gui():
    second = tk.Toplevel(root)
    second.geometry("400x400")

    tk.Label(second,text="Directory",font=("Arial",13)).pack()
    directory_text = tk.Text(second,height=1,width=40)
    directory_text.insert("1.0","CSVDATA/to_be_added.csv")
    directory_text.pack()

    button1 = tk.Button(second,text="ADD CONTENT to DATABASE",width=25,height=3,font=("Arial",14),
                        command=lambda:add_from_file(str(directory_text.get("1.0",END).rstrip())))
    button1.pack(pady=(100,0))

    second.mainloop()

def add_from_file(directory):
    conn = sqlite3.connect("student_database.db")

    # added = 0

    with open(directory,"r") as f:
        reader = csv.reader(f)

        for row in reader:
            last_name = row[0].upper()
            first_name = row[1].upper()
            middle_name = row[2].upper()
            student_no = row[3]
            course = row[4].upper()
            year = int(row[5])

            if student_no_exists(conn,student_no):
                continue
            insert_student(conn,last_name,first_name,middle_name,student_no,course,year)
            # added+=1

    conn.close()

    show_success(f"Successfully added to database")


def show_all_data_gui(tree):

    conn = sqlite3.connect("student_database.db")

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    conn.commit()
    conn.close()

    data = []

    for row in rows:
        data1 = [str(i) for i in row]
        course = data1.pop()
        data1[-1]+=f"-{course}"
        data.append(tuple(data1))

    for item in tree.get_children():
        tree.delete(item)

    for item in data:
        tree.insert("", END, values=item)
def main_gui():

    search = tk.Text(root, width=20, height=1,font=("Arial",12))
    search.pack(pady=(10,5))

    search_student_btn = tk.Button(root,width=14, text="Search", font=("Arial", 18),
                                   command=lambda: search_all_gui_second(tree,str(search.get("1.0",END).rstrip()).upper()))
    search_student_btn.pack()

    button4 = tk.Button(root,width=14,font=("Arial", 18), text="Show All", command=lambda :show_all_data_gui(tree))
    button4.pack()

    clear_btn = tk.Button(root, width=14, text="Clear", font=("Arial", 18),
                          command=lambda: clear_tree(tree))
    clear_btn.pack()

    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.LEFT, padx=10)


    add_btn = tk.Button(button_frame, width=12, font=("Arial", 18), text="Add a student", command=gui_add_first)
    add_btn.grid(row=0, column=0,pady=(5,10))

    add_file_btn = tk.Button(button_frame, width=12, font=("Arial", 18), text="Add from file",command=add_file_gui)
    add_file_btn.grid(row=1, column=0, pady=(5, 10))

    edit_button = tk.Button(button_frame, width=12, font=("Arial", 18), text="Edit",
                            command=lambda: gui_edit_second(tree))
    edit_button.grid(row=2, column=0, pady=(5, 10))

    delete_button = tk.Button(button_frame, width=12, font=("Arial", 18), text="Delete Record",
                              command=lambda: delete_gui(tree))
    delete_button.grid(row=3, column=0, pady=(5, 10))

    exit_btn = tk.Button(button_frame, width=12,font=("Arial", 18), text="Exit", command=exit)
    exit_btn.grid(row=4, column=0,pady=(5,10))


    tree = ttk.Treeview(root,
                        columns=("ID", "Last Name", "First Name", "Middle Name", "Student number", "Year-Course"),
                        show="headings")

    tree.heading("ID", text="ID")
    tree.heading("Last Name", text="Last Name")
    tree.heading("First Name", text="First Name")
    tree.heading("Student number", text="Student number")
    tree.heading("Year-Course", text="Year-Course")

    tree.pack(pady=(0, 10), padx=10, expand=True, fill="both")

    root.mainloop()

if __name__ == "__main__":
    main_gui()
