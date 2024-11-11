import csv
from model import Task
from datetime import datetime
import os


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
        if not os.path.exists(self.filename):
            return tasks
        try:
            with open(self.filename, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    if row:
                        try:
                            title, description, date_str, priority, task_id = row
                            date = datetime.strptime(date_str, "%Y-%m-%d")  # Konwersja daty
                            task = Task(title, description, date, int(priority), int(task_id))
                            tasks.append(task)
                        except ValueError as e:
                            print(f"Error parsing row {row}: {e}")
                            continue
        except Exception as e:
            print(f"Error reading file {self.filename}: {e}")

        if not tasks:
            print("No tasks found or file is empty.")
        return tasks


class PlannerController:
    def __init__(self):
        self.storage = CSVStorage()
        self.tasks = self.storage.load_tasks()
        self.task_id = max([task.id for task in self.tasks], default=0) + 1
        self.filtered_date = (None, None)
        self.filtered_priority = (None, None)
        self.sort_key = "date"
        self.sort_reverse = False

    def add_task(self, title, description, date, priority):
        if date:
            try:
                converted_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return "Error: Invalid date format. Please use 'YYYY-MM-DD'."
        else:
            converted_date = None

        if priority is not None:
            try:
                new_priority = int(priority)
                if new_priority < 1 or new_priority > 5:
                    raise ValueError("Priority must be between 1 and 5.")
            except ValueError:
                return "Priority must be a number between 1 and 5."
        else:
            new_priority = None

        task = Task(title, description, converted_date, new_priority, self.task_id)
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
            min_date, max_date = self.filtered_date
            if min_date and max_date:
                tasks = [task for task in tasks if min_date.date() <= task.date.date() <= max_date.date()]
            elif min_date:
                tasks = [task for task in tasks if task.date.date() >= min_date.date()]
            elif max_date:
                tasks = [task for task in tasks if task.date.date() <= max_date.date()]

        if self.filtered_priority:
            min_priority, max_priority = self.filtered_priority
            if min_priority is not None and max_priority is not None:
                tasks = [task for task in tasks if min_priority <= task.priority <= max_priority]
            elif min_priority is not None:
                tasks = [task for task in tasks if task.priority >= min_priority]
            elif max_priority is not None:
                tasks = [task for task in tasks if task.priority <= max_priority]

        return tasks

    def set_filter(self, min_date_input, max_date_input, min_priority_input, max_priority_input):
        try:
            if min_date_input:
                self.filtered_date = (datetime.strptime(min_date_input, "%Y-%m-%d"), self.filtered_date[1])
            if max_date_input:
                self.filtered_date = (self.filtered_date[0], datetime.strptime(max_date_input, "%Y-%m-%d"))
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD."

        if self.filtered_date[0] and self.filtered_date[1] and self.filtered_date[0] > self.filtered_date[1]:
            return "Minimum date cannot be later than maximum date."

        try:
            if min_priority_input:
                self.filtered_priority = (int(min_priority_input), self.filtered_priority[1])
            if max_priority_input:
                self.filtered_priority = (self.filtered_priority[0], int(max_priority_input))
        except ValueError:
            return "Invalid priority format. Please use integers between 1 and 5."

        if self.filtered_priority[0] and self.filtered_priority[1] and self.filtered_priority[0] > \
                self.filtered_priority[1]:
            return "Minimum priority cannot be greater than maximum priority."

        if not 1 <= self.filtered_priority[0] <= 5 or not 1 <= self.filtered_priority[1] <= 5:
            return "Priority must be between 1 and 5."

        return None

    def clear_filters(self):
        self.filtered_date = (None, None)
        self.filtered_priority = (None, None)

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

    def sort_tasks_by_key(self):
        if self.sort_key == "date":
            self.tasks.sort(key=lambda task: task.date, reverse=self.sort_reverse)
        elif self.sort_key == "priority":
            self.tasks.sort(key=lambda task: task.priority, reverse=self.sort_reverse)

    def get_min_max_dates(self):
        tasks_with_date = [task for task in self.tasks if task.date]

        if not tasks_with_date:
            return datetime.now().date(), datetime.now().date()

        min_date = min(tasks_with_date, key=lambda task: task.date).date
        max_date = max(tasks_with_date, key=lambda task: task.date).date
        return min_date, max_date

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            self.storage.save_tasks(self.tasks)
