import pyperclip
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from cam_flow import backend


def make_check(question, default, callback):
    txt = Label(text=question, size_hint=(0.7, 1))
    button = CheckBox(active=default, on_press=callback, size_hint=(0.1, 1))

    row = BoxLayout(orientation="horizontal", spacing=3)
    row.add_widget(txt)
    row.add_widget(button)
    return row, button


def make_path_check(img, callback):
    path = Button(text=img, size_hint=(0.7, 1), on_press=callback)
    check = CheckBox(
        size_hint=(0.1, 1),
        disabled=True,
        background_checkbox_disabled_down="atlas://data/images/defaulttheme/checkbox_on",
        background_checkbox_disabled_normal="atlas://data/images/defaulttheme/checkbox_off",
    )

    row = BoxLayout(orientation="horizontal", spacing=3)
    row.add_widget(path)
    row.add_widget(check)
    return row, check


class CamApp(App):
    COLOURS = {
        backend.FlowCell.STATUS.OUT_OF_SPEC: (1.0, 0.3, 0.3, 0.1),
        backend.FlowCell.STATUS.IN_PROGRESS: (0.2, 0.2, 0.8, 0.6),
        backend.FlowCell.STATUS.DONE: (0.4, 1.0, 0.4, 0.6),
        "ACTIVE": (0.0, 0.8, 0.0, 0.9),
    }

    def build(self):
        self.stack = backend.Stack("WER3")
        self.active_cell = None

        self.title = "Cam Flow"
        self.title_bar = BoxLayout(
            orientation="vertical", spacing=20, size_hint=(1.0, 0.1)
        )
        self.cell_label = Label(text="Hello world ")
        self.title_bar.add_widget(self.cell_label)

        self.main = GridLayout(rows=1, cols=2, spacing=20, size_hint=(1.0, 0.9))
        self.matrix = GridLayout(rows=12, cols=8, spacing=3,)
        self.questions = BoxLayout(orientation="vertical", spacing=3)

        self._make_matrix()
        self._make_questions()
        self.select_cell(("A", 1))(self.cell_buttons[("A", 1)])
        self._make_paths()

        self.main.add_widget(self.matrix)
        self.main.add_widget(self.questions)

        self.root = BoxLayout(orientation="vertical", padding=20,)
        self.root.add_widget(self.title_bar)
        self.root.add_widget(self.main)

        Window.bind(on_key_down=self._on_keyboard_down)

        updates_pr_second = 1
        Clock.schedule_interval(self.update, 1.0 / updates_pr_second)

        return self.root

    def move_focus(self, dx=0, dy=0):
        char, x = self.active_coordinate

        y = backend.Stack.rows.find(char)

        x += dx
        y += dy

        l, u = 1, len(backend.Stack.columns)
        x = l if x < l else u if x > u else x

        l, u = 0, len(backend.Stack.rows) - 1
        y = l if y < l else u if y > u else y

        char = backend.Stack.rows[y]
        coordinate = (char, x)

        self.select_cell(coordinate)(self.cell_buttons[coordinate])

    def _on_keyboard_down(self, *args):
        keyboard, scancode, codepoint, char, modifier = args
        if keyboard.command_keys.get(scancode, None) == "up":
            self.move_focus(dy=-1)
        if keyboard.command_keys.get(scancode, None) == "down":
            self.move_focus(dy=1)
        if keyboard.command_keys.get(scancode, None) == "left":
            self.move_focus(dx=-1)
        if keyboard.command_keys.get(scancode, None) == "right":
            self.move_focus(dx=1)
        if keyboard.command_keys.get(scancode, None) == "del":
            print("delete")
        if keyboard.command_keys.get(scancode, None) == "enter":
            print("enter")
        if keyboard.command_keys.get(scancode, None) == "tab":

            if self.active_cell.status == backend.FlowCell.STATUS.OUT_OF_SPEC:
                self.active_cell.status = backend.FlowCell.STATUS.IN_PROGRESS
            elif self.active_cell.status == backend.FlowCell.STATUS.IN_PROGRESS:
                self.active_cell.status = backend.FlowCell.STATUS.OUT_OF_SPEC
        self.update_matrix()

        return True

    def update(self, dt):
        self.active_cell.load_questions()
        for img, img_exists in self.active_cell.img_status.items():
            self.path_checks[img].active = img_exists

    def dump_callback(self, question):
        def dump(button):
            self.active_cell.questions[question] = button.active
            self.active_cell.dump_questions()

        return dump

    def _make_questions(self):
        self.question_boxes = {}
        for text, default in backend.FlowCell.DEFAULT_ANSWERS.items():
            question, button = make_check(text, default, self.dump_callback(text))
            self.questions.add_widget(question)
            self.question_boxes[text] = button

    def _make_paths(self):
        def cp(img):
            def f(instance):
                pyperclip.copy(str(self.active_cell.img_path(img).resolve()))

            return f

        self.path_checks = {}
        for img in backend.FlowCell.IMAGES:
            row, path_check = make_path_check(img, cp(img))
            self.path_checks[img] = path_check
            self.questions.add_widget(row)

    def _make_matrix(self):
        self.cell_buttons = {}
        for coordinate, _ in self.stack.cells.items():
            name = coordinate[0] + str(coordinate[1])
            button = Button(text=name, on_press=self.select_cell(coordinate))
            self.matrix.add_widget(button)
            self.cell_buttons[coordinate] = button

    def update_matrix(self):
        for _coordinate, button in self.cell_buttons.items():
            status = self.stack.cells[_coordinate].status
            button.background_color = self.COLOURS[status]

        self.cell_buttons[self.active_coordinate].background_color = self.COLOURS[
            "ACTIVE"
        ]

    def select_cell(self, coordinate):
        def f(instance):
            self.active_cell = self.stack.cells[coordinate]
            self.active_cell.load_questions()
            self.active_coordinate = coordinate
            self.cell_label.text = instance.text

            self.update_matrix()

            self.cell_buttons[self.active_coordinate].background_color = self.COLOURS[
                "ACTIVE"
            ]

            for question, value in self.active_cell.questions.items():
                self.question_boxes[question].active = value

        return f


if __name__ == "__main__":
    CamApp().run()
