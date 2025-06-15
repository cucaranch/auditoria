# to_do_list_db.py
import sqlite3
from datetime import datetime

# MEJORA: Añadir import de typing para type hints
# from typing import List, Dict, Optional

class Task:
    def __init__(self, id, title, description, due_date):
        # MEJORA: Añadir type hints (id: int, title: str, etc.)
        # MEJORA: Validar formato de fecha en el constructor
        # try:
        #     datetime.strptime(due_date, '%Y-%m-%d')
        # except ValueError:
        #     raise ValueError("Formato de fecha inválido. Use 'YYYY-MM-DD'")
        
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.completed = False

    def mark_as_completed(self):
        # MEJORA: Añadir type hint -> None
        self.completed = True

    def to_dict(self):
        # MEJORA: Añadir type hint -> Dict
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'completed': self.completed
        }

    @staticmethod
    def from_dict(task_dict):
        # MEJORA: Añadir type hint (task_dict: Dict) -> 'Task'
        # MEJORA: Validar campos requeridos en el diccionario
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
        # MEJORA: Añadir type hint (db_path: str)
        # MEJORA: Habilitar claves foráneas
        # self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    # MEJORA: Añadir métodos __enter__ y __exit__ para manejo de contexto
    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.close()
    
    # MEJORA: Añadir método close() para manejo explícito de conexión
    # def close(self):
    #     if self.conn:
    #         self.conn.commit()
    #         self.conn.close()
    #         self.conn = None

    def _create_table(self):
        # MEJORA: Añadir constraints NOT NULL y DEFAULT
        # MEJORA: Usar AUTOINCREMENT para IDs
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                               (id INTEGER PRIMARY KEY, title TEXT, description TEXT, due_date TEXT, completed BOOLEAN)''')
        self.conn.commit()

    def add_task(self, title, description, due_date):
        # MEJORA: Validar título no vacío
        # if not title.strip():
        #     raise ValueError("El título de la tarea no puede estar vacío")
        #
        # MEJORA: Validar formato de fecha
        # MEJORA: Devolver ID de la tarea creada (lastrowid)
        self.cursor.execute("INSERT INTO tasks (title, description, due_date, completed) VALUES (?, ?, ?, ?)",
                            (title, description, due_date, False))
        self.conn.commit()

    def remove_task(self, task_id):
        # MEJORA: Devolver boolean indicando si se eliminó la tarea
        self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()

    def get_task(self, task_id):
        # MEJORA: Añadir type hint -> Optional[Task]
        # MEJORA: Convertir el campo completed a boolean
        self.cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = self.cursor.fetchone()
        if row:
            return Task(row[0], row[1], row[2], row[3])
        return None

    # MEJORA: Añadir método específico para marcar tareas como completadas
    # def mark_task_completed(self, task_id):
    #     self.cursor.execute(
    #         "UPDATE tasks SET completed=1 WHERE id=? AND completed=0",
    #         (task_id,)
    #     )
    #     self.conn.commit()
    #     return self.cursor.rowcount > 0

    def list_tasks(self):
        # MEJORA: Ordenar tareas por fecha
        # MEJORA: Convertir completed a boolean
        self.cursor.execute("SELECT * FROM tasks")
        rows = self.cursor.fetchall()
        return [Task(row[0], row[1], row[2], row[3]).to_dict() for row in rows]

    def overdue_tasks(self):
        # MEJORA: Ordenar resultados por fecha
        now = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT * FROM tasks WHERE due_date < ? AND completed = 0", (now,))
        rows = self.cursor.fetchall()
        return [Task(row[0], row[1], row[2], row[3]) for row in rows]

    def upcoming_tasks(self):
        # MEJORA: Permitir especificar rango de días
        now = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT * FROM tasks WHERE due_date >= ?", (now,))
        rows = self.cursor.fetchall()
        return [Task(row[0], row[1], row[2], row[3]) for row in rows]

if __name__ == "__main__":
    # MEJORA: Usar manejo de contexto (with)
    todo_list = ToDoList()

    # MEJORA: Manejar posibles errores de validación
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

    # PROBLEMA: Acceso admin inseguro - DEBERÍA ELIMINARSE
    admin_conn = sqlite3.connect('tasks.db')
    admin_cursor = admin_conn.cursor()
    admin_cursor.execute("UPDATE tasks SET title='Admin Task' WHERE id=1")
    admin_conn.commit()
    admin_conn.close()

    print("\nTasks after admin update:")
    for task in todo_list.list_tasks():
        print(task)


        