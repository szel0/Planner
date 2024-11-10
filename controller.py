import csv
from model import Task
from datetime import datetime


class CSVStorage:
    def __init__(self, filename="tasks.csv"):
        self.filename = filename

    def save_tasks(self, tasks):
        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Description", "Date", "Priority", "ID"])
            for task in tasks:
                writer.writerow([task.title, task.description, task.date.strftime("%Y-%m-%d"), task.priority, task.id])

    def load_tasks(self):
        tasks = []
        try:
            with open(self.filename, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row:
                        title, description, date_str, priority, task_id = row
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        task = Task(title, description, date, int(priority), int(task_id))
                        tasks.append(task)
        except FileNotFoundError:
            print("No task file found, starting with empty list.")
        return tasks


class PlannerController:
    def __init__(self):
        self.storage = CSVStorage()
        self.tasks = self.storage.load_tasks()
        self.task_id = max([task.id for task in self.tasks], default=0) + 1
        self.filtered_date = None
        self.filtered_priority = None

    def add_task(self, title, description, date, priority):
        if not date:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            task_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format. Please use 'YYYY-MM-DD'."

        if priority < 1 or priority > 5:
            return "Error: Priority must be between 1 and 5."

        task = Task(title, description, task_date, priority, self.task_id)
        self.tasks.append(task)
        self.task_id += 1
        self.storage.save_tasks(self.tasks)
        return None

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_filtered_tasks(self):
        tasks = self.tasks

        if self.filtered_date:
            # Porównaj tylko datę, bez godziny
            tasks = [task for task in tasks if task.date.date() == self.filtered_date]

        if self.filtered_priority is not None:
            tasks = [task for task in tasks if task.priority == self.filtered_priority]

        return tasks

    def set_filter(self, date_input=None, priority_input=None):
        if date_input:
            try:
                self.filtered_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            except ValueError:
                return "Invalid Date format!"

        if priority_input:
            try:
                priority = int(priority_input)
                if 1 <= priority <= 5:
                    self.filtered_priority = priority
                else:
                    return "Priority must be between 1 and 5."
            except ValueError:
                return "Invalid Priority!"

        return None

    def clear_filters(self):
        self.filtered_date = None
        self.filtered_priority = None

    def edit_task(self, task, new_title=None, new_description=None, new_date=None, new_priority=None):
        if new_title:
            task.title = new_title
        if new_description:
            task.description = new_description

        if new_date:
            try:
                task.date = datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                return "Error: Invalid date format. Please use 'YYYY-MM-DD'."

        if new_priority is not None:
            try:
                new_priority = int(new_priority)
                if new_priority < 1 or new_priority > 5:
                    raise ValueError("Priority must be between 1 and 5.")
            except ValueError:
                return "Priority must be a number between 1 and 5."

            task.priority = new_priority

        self.storage.save_tasks(self.tasks)
        return None

    def sort_tasks_by_date(self, reverse=False):
        self.tasks.sort(key=lambda task: task.date, reverse=reverse)

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.storage.save_tasks(self.tasks)
