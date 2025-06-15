# to_do_list.py
import json
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
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description, due_date):
        new_task = Task(self.next_id, title, description, due_date)
        self.tasks.append(new_task)
        self.next_id += 1

    def remove_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                self.tasks.remove(task)
                break

    def get_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def list_tasks(self):
        return [task.to_dict() for task in self.tasks]

    def save_to_file(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.list_tasks(), file)

    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            tasks_list = json.load(file)
            self.tasks = [Task.from_dict(task_dict) for task_dict in tasks_list]

    def overdue_tasks(self):
        now = datetime.now()
        return [task for task in self.tasks if datetime.strptime(task.due_date, '%Y-%m-%d') < now and not task.completed]

    def upcoming_tasks(self):
        now = datetime.now()
        return [task for task in self.tasks if datetime.strptime(task.due_date, '%Y-%m-%d') >= now]

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

    todo_list.save_to_file('tasks.json')

    new_todo_list = ToDoList()
    new_todo_list.load_from_file('tasks.json')

    print("\nLoaded Tasks:")
    for task in new_todo_list.list_tasks():
        print(task)
