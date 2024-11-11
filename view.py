from datetime import datetime
from textual.app import App, on
from textual.containers import Grid, Horizontal, Vertical
from textual.widgets import Footer, Header, DataTable, Label, Button, Static, Input
from textual.screen import Screen


class PlannerApp(App):
    CSS_PATH = "styles.tcss"

    SORT_TYPES = ["Sort By: Date ASC", "Sort By: Date DESC", "Sort By: Priority ASC", "Sort By: Priority DESC"]

    BINDINGS = [
        ("s", "sort", "Change Sorting Type"),
        ("f", "filter", "Filter"),
        ("a", "add_task", "Add Task"),
        ("e", "edit_task", "Edit Task"),
        ("d", "delete_task", "Delete Task"),
        ("q", "quit_app", "Quit"),
    ]

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.tasks_table = DataTable()
        self.sort_index = 0

    def compose(self):
        yield Header()
        self.tasks_table.add_columns("Title", "Description", "Date", "Priority")
        self.tasks_table.zebra_stripes = True
        self.tasks_table.cursor_type = "row"
        self.tasks_table.focus()

        buttons_panel = Vertical(
            Button(self.SORT_TYPES[self.sort_index], variant="default", id="sort"),
            Button("Filter", variant="default", id="filter"),
            Button("Add Task", variant="success", id="add_task"),
            Button("Edit Task", variant="primary", id="edit_task"),
            Button("Delete Task", variant="error", id="delete_task"),
            Static(classes="separator"),
        )

        yield Horizontal(buttons_panel, self.tasks_table)
        yield Footer()
        yield Label("", id="title")

    def on_mount(self):
        self.title = "Task Planner"
        self.sub_title = "Manage your tasks"
        self.load_tasks()

    def load_tasks(self):
        tasks_table = self.query_one(DataTable)
        tasks_table.clear()
        self.controller.sort_tasks_by_key()
        tasks = self.controller.get_filtered_tasks()

        for task in tasks:
            tasks_table.add_row(
                task.title,
                task.description,
                task.date.strftime("%Y-%m-%d"),
                task.priority,
                key=task.id
            )
        self.query_one("#title").update("")

    @on(Button.Pressed, "#sort")
    def action_sort(self):
        self.sort_index = (self.sort_index + 1) % len(self.SORT_TYPES)
        self.query_one("#sort").label = self.SORT_TYPES[self.sort_index]

        if self.sort_index == 0:
            self.controller.sort_key = "date"
            self.controller.sort_reverse = False
        elif self.sort_index == 1:
            self.controller.sort_key = "date"
            self.controller.sort_reverse = True
        elif self.sort_index == 2:
            self.controller.sort_key = "priority"
            self.controller.sort_reverse = False
        elif self.sort_index == 3:
            self.controller.sort_key = "priority"
            self.controller.sort_reverse = True

        self.load_tasks()

    @on(Button.Pressed, "#filter")
    def action_filter(self):
        self.push_screen(FilterDialog(self.controller))

    @on(Button.Pressed, "#add_task")
    def action_add_task(self):
        self.push_screen(AddTaskDialog(self.controller))

    @on(Button.Pressed, "#edit_task")
    def action_edit_task(self):
        tasks = self.query_one(DataTable)

        if not tasks.rows:
            self.query_one("#title").update("No tasks available to edit.")
            return

        try:
            cell_key = tasks.coordinate_to_cell_key(tasks.cursor_coordinate)
            row_key = cell_key.row_key

            if row_key:
                self.push_screen(EditTaskDialog(self.controller, row_key.value))
        except IndexError:
            self.query_one("#title").update("No task selected.")

    @on(Button.Pressed, "#delete_task")
    def action_delete_task(self):
        tasks = self.query_one(DataTable)

        if not tasks.rows:
            self.query_one("#title").update("No tasks available to delete.")
            return

        try:
            cell_key = tasks.coordinate_to_cell_key(tasks.cursor_coordinate)
            row_key = cell_key.row_key

            if row_key:
                self.push_screen(DeleteConfirm(self.controller, row_key.value))
        except IndexError:
            self.query_one("#title").update("No task selected.")

    def action_quit_app(self):
        self.exit()


class FilterDialog(Screen):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def compose(self):

        min_date, max_date = self.controller.get_min_max_dates()

        min_date_value = self.controller.filtered_date[0].strftime("%Y-%m-%d") \
            if self.controller.filtered_date[0] else min_date.strftime("%Y-%m-%d")
        max_date_value = self.controller.filtered_date[1].strftime("%Y-%m-%d") \
            if self.controller.filtered_date[1] else max_date.strftime("%Y-%m-%d")
        min_priority_value = str(self.controller.filtered_priority[0]) \
            if self.controller.filtered_priority[0] else "1"
        max_priority_value = str(self.controller.filtered_priority[1]) \
            if self.controller.filtered_priority[1] else "5"

        yield Grid(
            Label("Filter Tasks", id="title"),
            Label("Filter by Minimum Date (YYYY-MM-DD):"),
            Input(value=min_date_value, id="input_min_date"),
            Label("Filter by Maximum Date (YYYY-MM-DD):"),
            Input(value=max_date_value, id="input_max_date"),
            Label("Filter by Minimum Priority (1-5):"),
            Input(value=min_priority_value, id="input_min_priority"),
            Label("Filter by Maximum Priority (1-5):"),
            Input(value=max_priority_value, id="input_max_priority"),
            Label("Filter by Name:"),
            Input(value=self.controller.filtered_name, id="input_name"),
            Button("Clear Filters", variant="default", id="clear_filters"),
            Button("Apply", variant="success", id="apply"),
            id="filter-dialog"
        )

    @on(Button.Pressed, "#clear_filters")
    def clear_filters(self):
        self.controller.clear_filters()

        input_min_date = self.query_one("#input_min_date")
        input_max_date = self.query_one("#input_max_date")
        input_min_priority = self.query_one("#input_min_priority")
        input_max_priority = self.query_one("#input_max_priority")
        input_name = self.query_one("#input_name")


        min_date, max_date = self.controller.get_min_max_dates()

        input_min_date.value = min_date.strftime("%Y-%m-%d")
        input_max_date.value = max_date.strftime("%Y-%m-%d")
        input_min_priority.value = "1"
        input_max_priority.value = "5"
        input_name.value = ""

    @on(Button.Pressed, "#apply")
    def apply_filter(self):
        min_date_input = self.query_one("#input_min_date").value
        max_date_input = self.query_one("#input_max_date").value
        min_priority_input = self.query_one("#input_min_priority").value
        max_priority_input = self.query_one("#input_max_priority").value
        name_input = self.query_one("#input_name").value

        min_date, max_date = self.controller.get_min_max_dates()

        error_message = (self.controller.set_filter(
            min_date_input or min_date.strftime("%Y-%m-%d"),
            max_date_input or max_date.strftime("%Y-%m-%d"),
            min_priority_input or "1",
            max_priority_input or "5",
            name_input
        ))

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
        priority = self.query_one("#input_priority").value or "3"

        error_message = self.controller.add_task(title, description, date, priority)

        if error_message:
            self.query_one("#title").update(f"{error_message}")
        else:
            self.app.pop_screen()
            self.app.load_tasks()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()


class EditTaskDialog(Screen):
    def __init__(self, controller, task_id):
        super().__init__()
        self.controller = controller
        self.current_task = self.controller.get_task_by_id(task_id)

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
            new_title,
            new_description,
            new_date,
            new_priority
        )

        if error_message:
            self.query_one("#title").update(error_message)
        else:
            self.app.pop_screen()
            self.app.load_tasks()

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
        self.controller.delete_task(self.task_id)
        self.app.pop_screen()
        self.app.load_tasks()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
