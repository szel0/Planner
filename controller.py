from model import Task, Calendar, Priority


class PlannerController:
    def __init__(self):
        self.calendar = Calendar()

    def add_task(self, title, description, date, priority=Priority.MEDIUM):
        task = Task(title, description, date, priority)
        self.calendar.add_task(task)
        print(f"Task '{task.title}' added for {task.date.strftime('%Y-%m-%d')}.")

    def get_tasks_for_day(self, date):
        tasks = self.calendar.get_tasks_for_day(date)
        if tasks:
            for task in tasks:
                print(f"Task: {task.title} - {task.description} (Priority: {task.priority})")
        else:
            print(f"No tasks for {date}.")

    def edit_task(self, task, new_title=None, new_description=None, new_date=None, new_priority=None):
        if new_title:
            task.title = new_title
        if new_description:
            task.description = new_description
        if new_date:
            task.date = new_date
        if new_priority:
            task.priority = new_priority
        print(f"Task '{task.title}' has been updated.")

    def delete_task(self, task):
        if task in self.calendar.tasks.get(task.date, []):
            self.calendar.tasks[task.date].remove(task)
            print(f"Task '{task.title}' has been deleted.")
        else:
            print(f"Task not found.")

if __name__ == "__main__":
    controller = PlannerController()

    # Przykładowe dodawanie zadań
    controller.add_task("Meeting with Bob", "Discuss project milestones", "2024-11-10", Priority.HIGH)
    controller.add_task("Grocery shopping", "Buy groceries for the week", "2024-11-10", Priority.MEDIUM)

    # Pobieranie zadań na określony dzień
    controller.get_tasks_for_day("2024-11-10")