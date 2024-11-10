from datetime import datetime
from textual.app import App, on
from textual.containers import Grid, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Footer, Header, DataTable, Label, Button, Static, Input
from textual.screen import Screen


class PlannerApp(App):
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        ("f", "filter", "Filter"),
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
            Button("Filter", variant="default", id="filter"),
            Button("Add Task", variant="success", id="add_task"),
            Button("Edit Task", variant="primary", id="edit_task"),
            Button("Delete Task", variant="error", id="delete_task"),
            Static(classes="separator"),
        )

        yield Horizontal(buttons_panel, tasks_table)
        yield Footer()
        yield Label("", id="title")

    def on_mount(self):
        self.title = "Task Planner"
        self.sub_title = "Manage your tasks"
        self.load_tasks()

    def load_tasks(self):
        tasks_table = self.query_one(DataTable)
        tasks_table.clear()
        self.controller.sort_tasks_by_date()
        tasks = self.controller.get_filtered_tasks()

        for task in tasks:
            tasks_table.add_row(task.title, task.description, task.date.strftime("%Y-%m-%d"), task.priority)

    @on(Button.Pressed, "#filter")
    def action_filter(self):
        self.push_screen(FilterDialog(self.controller))

    @on(Button.Pressed, "#add_task")
    def action_add_task(self):
        self.push_screen(AddTaskDialog(self.controller))

    @on(Button.Pressed, "#edit_task")
    def action_edit_task(self):
        if self.controller.tasks:
            self.push_screen(TaskListScreen(self.controller, True))
        else:
            self.query_one("#title").update("No tasks to edit")

    @on(Button.Pressed, "#delete_task")
    def action_delete_task(self):
        if self.controller.tasks:
            self.push_screen(TaskListScreen(self.controller, False))
        else:
            self.query_one("#title").update("No tasks to delete")


class FilterDialog(Screen):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def compose(self):

        date_placeholder = self.controller.filtered_date.strftime(
            "%Y-%m-%d") if self.controller.filtered_date else "YYYY-MM-DD"
        priority_placeholder = str(
            self.controller.filtered_priority) if self.controller.filtered_priority is not None else "1-5"

        yield Grid(
            Label("Filter Tasks", id="title"),
            Label("Filter by Date (YYYY-MM-DD):"),
            Input(placeholder=date_placeholder, id="input_date"),
            Label("Filter by Priority (1-5):"),
            Input(placeholder=priority_placeholder, id="input_priority"),
            Button("Clear Filters", variant="default", id="clear_filters"),
            Button("Apply", variant="success", id="apply"),
            id="filter-dialog"
        )

    @on(Button.Pressed, "#clear_filters")
    def clear_filters(self):
        self.controller.clear_filters()

        input_date = self.query_one("#input_date")
        input_priority = self.query_one("#input_priority")

        input_date.placeholder = "YYYY-MM-DD"
        input_priority.placeholder = "1-5"

    @on(Button.Pressed, "#apply")
    def apply_filter(self):
        date_input = self.query_one("#input_date").value
        priority_input = self.query_one("#input_priority").value

        error_message = self.controller.set_filter(date_input, priority_input)

        if error_message:
            self.query_one("#title").update(error_message)
        else:
            self.app.pop_screen()
            self.app.load_tasks()


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
            Input(placeholder="3", id="input_priority"),
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
        priority = int(self.query_one("#input_priority").value or 3)

        error_message = self.controller.add_task(title, description, date, priority)

        if error_message:
            self.query_one("#title").update(f"{error_message}")
        else:
            self.app.pop_screen()
            self.app.load_tasks()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class TaskListScreen(Screen):
    def __init__(self, controller, edit):
        super().__init__()
        self.controller = controller
        self.edit = edit

    def compose(self):
        buttons = [Button(f"{task.title} {task.date.strftime('%Y-%m-%d')}", id=f"task_{task.id}")
                   for task in self.controller.get_filtered_tasks()]

        yield ScrollableContainer(*buttons, id="task_list")

        yield Button("Cancel", variant="error", id="cancel")

    @on(Button.Pressed)
    def on_task_button_pressed(self, message: Button.Pressed):
        if not message.button.id.startswith("task_"):
            return

        task_id = int(message.button.id.split("_")[1])
        task = self.controller.get_task_by_id(task_id)

        if task and self.edit:
            self.app.pop_screen()
            self.app.push_screen(EditTaskDialog(self.controller, task))
        if task and not self.edit:
            self.app.pop_screen()
            self.app.push_screen(DeleteConfirm(self.controller, task))

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class EditTaskDialog(Screen):
    def __init__(self, controller, task):
        super().__init__()
        self.controller = controller
        self.current_task = task

    def compose(self):
        yield Grid(
            Label("Edit Task", id="title"),
            Label("Title:"),
            Input(value=self.current_task.title, id="input_title"),
            Label("Description:"),
            Input(value=self.current_task.description, id="input_description"),
            Label("Date:"),
            Input(value=self.current_task.date.strftime("%Y-%m-%d"), id="input_date"),
            Label("Priority:"),
            Input(value=str(self.current_task.priority), id="input_priority"),
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
        new_priority = self.query_one("#input_priority").value

        error_message = self.controller.edit_task(
            self.current_task,
            new_title=new_title,
            new_description=new_description,
            new_date=new_date,
            new_priority=new_priority
        )

        if error_message:
            self.query_one("#title").update(error_message)
        else:
            self.app.pop_screen()
            self.app.load_tasks()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
        self.app.push_screen(TaskListScreen(self.controller, True))


class DeleteConfirm(Screen):
    def __init__(self, controller, task):
        super().__init__()
        self.controller = controller
        self.current_task = task

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
        self.controller.delete_task(self.current_task)
        self.app.pop_screen()
        self.app.load_tasks()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
