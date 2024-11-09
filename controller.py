from model import Task, Calendar, Priority
from datetime import datetime


class PlannerController:
    def __init__(self):
        self.calendar = Calendar()

    def add_task(self, title, description, date, priority=Priority.MEDIUM):

        if not date:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            task_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return "Error: Invalid date format. Please use 'YYYY-MM-DD'."

        task = Task(title, description, task_date, priority)
        self.calendar.add_task(task)
        return None

    def get_tasks_for_day(self, date):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.calendar.get_tasks_for_day(date)

    def edit_task(self, task, new_title=None, new_description=None, new_date=None, new_priority=None):
        if new_title:
            task.title = new_title
        if new_description:
            task.description = new_description
        if new_date:
            task.date = new_date
        if new_priority:
            task.priority = new_priority

    def delete_task(self, task):
        if task in self.calendar.tasks.get(task.date, []):
            self.calendar.tasks[task.date].remove(task)
