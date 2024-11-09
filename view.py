from datetime import datetime
from textual.app import App, on
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Footer, Header, DataTable, Label, Button, Static, Input
from textual.screen import Screen
from model import Priority


class PlannerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("a", "add_task", "Add Task"),
        ("e", "edit_task", "Edit Task"),
        ("d", "delete_task", "Delete Task"),
        ("q", "quit_app", "Quit"),
    ]

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def action_quit_app(self):
        self.exit()

    def compose(self):
        yield Header()
        tasks_table = DataTable()
        tasks_table.focus()
        tasks_table.add_columns("Title", "Description", "Date", "Priority")
        tasks_table.zebra_stripes = True
        tasks_table.cursor_type = "row"

        buttons_panel = Vertical(
            Button("Add Task", variant="success", id="add_task"),
            Button("Edit Task", variant="primary", id="edit_task"),
            Button("Delete Task", variant="error", id="delete_task"),
            Static(classes="separator"),
        )

        yield Horizontal(tasks_table, buttons_panel)
        yield Footer()

    def on_mount(self):
        self.title = "Task Planner"
        self.sub_title = "Manage your tasks"
        self._load_tasks()

    def _load_tasks(self):
        tasks_table = self.query_one(DataTable)
        tasks_table.clear()
        date = datetime.now().strftime("%Y-%m-%d")  # Example: today's tasks
        tasks = self.controller.get_tasks_for_day(date)

        for task in tasks:
            tasks_table.add_row(task.title, task.description, task.date.strftime("%Y-%m-%d"), task.priority)

    @on(Button.Pressed, "#add_task")
    def action_add_task(self):
        self.push_screen(AddTaskDialog(self.controller))

    @on(Button.Pressed, "#edit_task")
    def action_edit_task(self):
        tasks_table = self.query_one(DataTable)
        cell_key = tasks_table.coordinate_to_cell_key(tasks_table.cursor_coordinate)
        row_key = cell_key.row_key

        if row_key:
            task = self.controller.get_task_by_id(row_key.value)
            self.push_screen(EditTaskDialog(self.controller, task))

    @on(Button.Pressed, "#delete_task")
    def action_delete_task(self):
        tasks_table = self.query_one(DataTable)
        cell_key = tasks_table.coordinate_to_cell_key(tasks_table.cursor_coordinate)
        row_key = cell_key.row_key

        if row_key:
            self.push_screen(DeleteConfirm(self.controller, row_key.value))


class AddTaskDialog(Screen):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def compose(self):
        today_date = datetime.now().strftime("%Y-%m-%d")
        yield Grid(
            Label("Add Task", id="title"),
            Label("Title:"),
            Input(placeholder="Task Title", id="input_title"),
            Label("Description:"),
            Input(placeholder="Task Description", id="input_description"),
            Label("Date:"),
            Input(placeholder=today_date, id="input_date"),
            Label("Priority:"),
            Input(placeholder=str(Priority.MEDIUM), id="input_priority"),
            Static(),
            Button("Cancel", variant="error", id="cancel"),
            Button("Ok", variant="success", id="ok"),
            id="input-dialog",
        )

    @on(Button.Pressed, "#ok")
    def submit(self):
        title = self.query_one("#input_title").value or "Task Title"
        description = self.query_one("#input_description").value or "Task Description"
        date = self.query_one("#input_date").value or datetime.now().strftime("%Y-%m-%d")
        priority = int(self.query_one("#input_priority").value or Priority.MEDIUM)

        # Próbujemy dodać zadanie i łapiemy błędy
        error_message = self.controller.add_task(title, description, date, priority)

        if error_message:
            # Jeśli wystąpił błąd, wyświetl komunikat w tytule
            self.query_one("#title").update(f"{error_message}")  # Wyświetlamy błąd w nagłówku
        else:
            # Jeśli zadanie zostało dodane poprawnie, zamykamy ekran
            self.app.pop_screen()
            self.app._load_tasks()


    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class EditTaskDialog(Screen):
    def __init__(self, controller, task):
        super().__init__()
        self.controller = controller
        self.task = task

    def compose(self):
        yield Grid(
            Label("Edit Task", id="title"),
            Label("Title:"),
            Input(value=self.task.title, id="input_title"),
            Label("Description:"),
            Input(value=self.task.description, id="input_description"),
            Label("Date:"),
            Input(value=self.task.date.strftime("%Y-%m-%d"), id="input_date"),
            Label("Priority:"),
            Input(value=str(self.task.priority), id="input_priority"),
            Static(),
            Button("Cancel", variant="error", id="cancel"),
            Button("Save", variant="success", id="save"),
            id="edit-dialog",
        )

    @on(Button.Pressed, "#save")
    def save(self):
        new_title = self.query_one("#input_title").value
        new_description = self.query_one("#input_description").value
        new_date = self.query_one("#input_date").value
        new_priority = int(self.query_one("#input_priority").value or self.task.priority)

        # Update the task using the controller
        self.controller.edit_task(
            self.task,
            new_title=new_title,
            new_description=new_description,
            new_date=new_date,
            new_priority=new_priority
        )
        self.app.pop_screen()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class DeleteConfirm(Screen):
    def __init__(self, controller, task_id):
        super().__init__()
        self.controller = controller
        self.task_id = task_id

    def compose(self):
        yield Grid(
            Label("Confirm Deletion", id="title"),
            Label("Are you sure you want to delete this task?", id="confirmation"),
            Static(),
            Button("Cancel", variant="error", id="cancel"),
            Button("Delete", variant="success", id="confirm"),
            id="confirm-dialog"
        )

    @on(Button.Pressed, "#confirm")
    def delete(self):
        task = self.controller.get_task_by_id(self.task_id)
        self.controller.delete_task(task)
        self.app.pop_screen()
        self.app._load_tasks()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
