# to_do_list.py
import json# se debe cambiar por un import  sqlite3
from datetime import datetime

class Task:
    def __init__(self, id, title, description, due_date):
         
        # - No valida tipos (¿title es str?, ¿due_date es fecha válida?).
        # - Si `id` es None, puede causar problemas en SQLite (debe ser AUTOINCREMENT).
        # - `completed` debería ser un parámetro opcional (no siempre False).
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date  # Riesgo: Si due_date no es "YYYY-MM-DD", fallará después.
        self.completed = False

    def mark_as_completed(self): 
        # - No verifica si ya estaba completada.
        # - No retorna estado de éxito/fallo.
        self.completed = True

class ToDoList:
    def __init__(self):
        self.tasks = []  # QA: Ineficiente para búsquedas (debería ser dict o SQLite).
        self.next_id = 1  # Riesgo: En SQLite, el ID debe manejarse con AUTOINCREMENT.

    def add_task(self, title, description, due_date):
        # - No valida si `title` está vacío o `due_date` es válida.
        # - Si hay un error, `next_id` ya se incrementó (inconsistencia).
        new_task = Task(self.next_id, title, description, due_date)
        self.tasks.append(new_task)
        self.next_id += 1

    def remove_task(self, task_id):
        # - Ineficiente (recorre lista completa, O(n)).
        # - Si hay duplicados, solo borra el primero.
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                break  # Solo elimina la primera coincidencia.

    def get_task(self, task_id):
        # - Retorna `None` silenciosamente (debería lanzar excepción).
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def save_to_file(self, file_path):
        # - No maneja errores de escritura/permisos.
        # - No verifica si el archivo ya existe.
        with open(file_path, 'w') as file:
            json.dump(self.list_tasks(), file)  # Sin formato legible (falta `indent=2`).

    def load_from_file(self, file_path):
        # - No verifica si el archivo existe.
        # - Si el JSON está corrupto, el programa crashea.
        # - No actualiza `next_id` correctamente (puede generar IDs duplicados).
        with open(file_path, 'r') as file:
            tasks_list = json.load(file)
            self.tasks = [Task.from_dict(task_dict) for task_dict in tasks_list]

#-----------------------------------------------------------------------------------------------
# CAMBIO 1: Reemplazar json por sqlite3 para persistencia en base de datos
# Antes: import json
import sqlite3  #  Nueva importación para manejo de base de datos
from datetime import datetime
from typing import List, Optional  # Mejorar tipado de datos

class Task:
    def __init__(self, id: int, title: str, description: str, due_date: str, completed: bool = False):
        #  Mejora: Añadir type hints y hacer completed opcional
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date  #  Se debe validar formato (se implementará después)
        self.completed = completed

    def mark_as_completed(self) -> None:  #  Mejora: Añadir type hint
        self.completed = True

    def to_dict(self) -> dict:  #  Mantener para compatibilidad
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date,
            'completed': self.completed
        }

    @staticmethod
    def from_dict(task_dict: dict) -> 'Task':  #  Mejora: Type hint y validación
        #  Validación añadida en versión SQLite
        return Task(
            task_dict['id'],
            task_dict['title'],
            task_dict['description'],
            task_dict['due_date'],
            task_dict.get('completed', False)
        )

class ToDoList:
    def __init__(self, db_path: str = 'todo.db'):  #  Nueva parametrización
        #  CAMBIO 2: Reemplazar lista en memoria por conexión SQLite
        # Antes: 
        # self.tasks = []  
        # self.next_id = 1
        
        #  Nueva implementación:
        self.db_path = db_path
        self.conn = self._initialize_db()
        
    def _initialize_db(self) -> sqlite3.Connection:
        """ Paso 1: Inicializar base de datos y crear tabla si no existe"""
        conn = sqlite3.connect(self.db_path)
        
        # Paso 2: Configuraciones de seguridad importantes
        conn.execute("PRAGMA foreign_keys = ON")  #  Habilitar integridad referencial
        conn.execute("PRAGMA secure_delete = ON")  #  Borrado seguro de datos
        
        #  Paso 3: Crear estructura de tabla (similar al JSON original pero en SQL)
        conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     title TEXT NOT NULL,
                     description TEXT,
                     due_date TEXT NOT NULL,
                     completed BOOLEAN DEFAULT FALSE)''')
        conn.commit()
        return conn

    def add_task(self, title: str, description: str, due_date: str) -> Task:
        """ Paso 4: Reimplementar con validaciones y SQL"""
        #  añadir validación  (no existía en versión JSON)
        if not title or not isinstance(title, str):
            raise ValueError("El título debe ser un string no vacío")
            
        try:
            datetime.strptime(due_date, '%Y-%m-%d')  # Validar formato fecha
        except ValueError:
            raise ValueError("Formato de fecha debe ser YYYY-MM-DD")

        try:
            #  CAMBIO 3: Reemplazar append a lista por INSERT SQL
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO tasks (title, description, due_date)
                           VALUES (?, ?, ?)''', 
                           (title.strip(), 
                            description.strip() if description else None, 
                            due_date))
            self.conn.commit()
            
            #  Obtener ID automático (mejor que next_id manual)
            return Task(cursor.lastrowid, title, description, due_date)
        except sqlite3.Error as e:
            print(f"Error al agregar tarea: {e}")
            raise

    def remove_task(self, task_id: int) -> bool:
        """ Paso 5: Implementar DELETE seguro"""
        try:
            with self.conn:  #  Usar transacción automática
                cursor = self.conn.cursor()
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                return cursor.rowcount > 0  #  Retornar si se eliminó algo
        except sqlite3.Error as e:
            print(f"Error al eliminar tarea: {e}")
            return False

    #  CAMBIO 4: Mantener métodos existentes pero reimplementar con SQL
    def get_task(self, task_id: int) -> Optional[Task]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        return Task(*row) if row else None  #  Mejor manejo que versión JSON

    def list_tasks(self) -> List[Task]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        return [Task(*row) for row in cursor.fetchall()]  #  Más eficiente que JSON

    #  CAMBIO 5: Métodos especializados con filtros SQL
    def overdue_tasks(self) -> List[Task]:
        today = datetime.now().strftime('%Y-%m-%d')
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM tasks 
                       WHERE due_date < ? AND completed = FALSE''', (today,))
        return [Task(*row) for row in cursor.fetchall()]  #  Filtro en SQL, no en Python

    #  Paso 6: Implementar cierre seguro de conexión
    def close(self):
        if self.conn:
            self.conn.close()

    #  Context manager para manejo seguro de recursos
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

#  CAMBIO 6: Eliminar métodos de JSON (save_to_file/load_from_file)
#  Se quitan porque ahora usamos SQLite

if __name__ == "__main__":
    #  Ejemplo de uso con SQLite
    with ToDoList() as todo_list:  #  Usar context manager
        # Testear funcionalidad básica
        task_id = todo_list.add_task("Nueva tarea", "Descripción", "2023-12-31")
        print(f"Tarea agregada con ID: {task_id}")
        
        # Marcar como completada (nuevo método mejorado)
        todo_list.mark_task_completed(task_id)
        
        print("\nTareas pendientes:")
        for task in todo_list.list_tasks():
            print(f"{task.id}: {task.title} ({'Completada' if task.completed else 'Pendiente'})")

