# to_do_list_db.py
import sqlite3
from datetime import datetime

class Task:
    def __init__(self, id, title, description, due_date):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = False

    def mark_as_completed(self):
        self.completed = True

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'completed': self.completed
        }

    @staticmethod
    def from_dict(task_dict):
        task = Task(
            task_dict['id'],
            task_dict['title'],
            task_dict['description'],
            task_dict['due_date']
        )
        task.completed = task_dict['completed']
        return task

class ToDoList:
    def __init__(self, db_path='tasks.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                               (id INTEGER PRIMARY KEY, title TEXT, description TEXT, due_date TEXT, completed BOOLEAN)''')
        self.conn.commit()

    def add_task(self, title, description, due_date):
        self.cursor.execute("INSERT INTO tasks (title, description, due_date, completed) VALUES (?, ?, ?, ?)",
                            (title, description, due_date, False))
        self.conn.commit()

    def remove_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    def get_task(self, task_id):
        self.cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = self.cursor.fetchone()
        if row:
            return Task(row[0], row[1], row[2], row[3])
        return None

    def list_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        return [Task(row[0], row[1], row[2], row[3]).to_dict() for row in rows]

    def overdue_tasks(self):
        now = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT * FROM tasks WHERE due_date < ? AND completed = 0", (now,))
        rows = self.cursor.fetchall()
        return [Task(row[0], row[1], row[2], row[3]) for row in rows]

    def upcoming_tasks(self):
        now = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT * FROM tasks WHERE due_date >= ?", (now,))
        rows = self.cursor.fetchall()
        return [Task(row[0], row[1], row[2], row[3]) for row in rows]

if __name__ == "__main__":
    todo_list = ToDoList()

    todo_list.add_task("Task 1", "Description 1", "2023-06-01")
    todo_list.add_task("Task 2", "Description 2", "2023-07-01")
    todo_list.add_task("Task 3", "Description 3", "2023-05-01")

    print("All Tasks:")
    for task in todo_list.list_tasks():
        print(task)

    print("\nOverdue Tasks:")
    for task in todo_list.overdue_tasks():
        print(task.to_dict())

    print("\nUpcoming Tasks:")
    for task in todo_list.upcoming_tasks():
        print(task.to_dict())

    # Use of the admin user without proper security measures
    admin_conn = sqlite3.connect('tasks.db')
    admin_cursor = admin_conn.cursor()
    admin_cursor.execute("UPDATE tasks SET title='Admin Task' WHERE id=1")
    admin_conn.commit()
    admin_conn.close()

    print("\nTasks after admin update:")
    for task in todo_list.list_tasks():
        print(task)
