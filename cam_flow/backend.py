from enum import Enum
import pathlib
from itertools import product
import json
import base64


class FlowCell:
    """Keep track of the state of a single flow cell.
    """

    IMAGES = [
        "Island_top",
        "Island_bottom",
        "Other",
    ]
    STATUS = Enum("STATUS", ["OUT_OF_SPEC", "IN_PROGRESS", "DONE",])

    DEFAULT_ANSWERS = {
        "Are the electrodes in the measurement channel damaged?": False,
        "Are there large visible particles, debris or artifacts near the electrodes in the measurement channel?": False,
        "Do the four white squares touch the middle white cross?": False,
        "Is there critical incomplete bond (within 20 µm of the boundary of the flow cell channel)?": False,
        "Is there damage on the inner channel boundary or is it not intact?": False,
    }

    def __init__(self, stack, grid_position, model="Q"):
        self.stack = stack
        self.grid_position = grid_position
        self.model = model

        self.questions = {
            k: w for k, w in FlowCell.DEFAULT_ANSWERS.items()
        }  # pass by value!
        self.status = FlowCell.STATUS.IN_PROGRESS

        self._base_path = self.stack._base_path / self.label

    @property
    def label(self):
        return f"{self.stack.name}-{self.grid_position}{self.model}"

    def dump_questions(self):
        self.mkdir()
        with (self._base_path / "questions.json").open("w") as f:
            json.dump(self.questions, f, sort_keys=True, indent=4)
        with (self._base_path / ".state").open("w") as f:
            json.dump(self.status.name, f)


    def load_questions(self):
        try:
            with (self._base_path / "questions.json").open("r") as f:
                self.questions = json.load(f)
            with (self._base_path / ".state").open("r") as f:
                name = json.load(f)
                self.status = FlowCell.STATUS[name]
        except:
            pass

    @property
    def img_status(self):
        return {img: self.img_path(img).exists() for img in FlowCell.IMAGES}

    def mkdir(self):
        self._base_path.mkdir(exist_ok=True, parents=True)

    def img_path(self, img):
        self.mkdir()
        return self._base_path / f"{img}.jpg"

    def encoded_img(self, img):
        if not self.img_path(img).exists():
            return None
        with self.img_path(img).open("rb") as image_file:
            return base64.b64encode(image_file.read())

    def as_payload(self):
        # https://qc-api.sbtinstruments.com/reports/?update=1
        answers = {**self.questions}
        for i, img in enumerate(FlowCell.IMAGES, start=1):
            answers[f"picture{i}"] = self.encoded_img(img)

        return {
            "answers": answers,
            "last_edited_by": 7,
            "reportID": 51,
            "status": "OK",
        }


class Stack:
    """Keep track of a collection of flow cells
    """

    rows = "ABCDEFGHIJKL"
    columns = list(range(1, 9))
    always_missing = [
        ("A", 1),
        ("A", 2),
        ("B", 1),
        ("A", 7),
        ("A", 8),
        ("B", 8),
        ("K", 1),
        ("L", 1),
        ("L", 2),
        ("K", 8),
        ("L", 7),
        ("L", 8),
    ]

    def __init__(self, name):
        self.name = name
        self._base_path = pathlib.Path.cwd() / f"{self.name}"

        self.cells = {
            (row, column): FlowCell(self, f"{row}{column}")
            for row, column in product(self.rows, self.columns)
        }

        for coordinate in self.always_missing:
            self.cells[coordinate].status = FlowCell.STATUS.OUT_OF_SPEC



    @property
    def _state_matrix(self):
        """Represent the stack as a string.

        This is for debugging and can be safely deleted.
        """
        cell_reps = {
            FlowCell.STATUS.OUT_OF_SPEC: "X",
            FlowCell.STATUS.IN_PROGRESS: ".",
            FlowCell.STATUS.DONE: "O",
        }

        rep = "   " + " ".join([str(column) for column in self.columns]) + "\n"
        for row in Stack.rows:
            row_rep = f"{row} "
            for column in Stack.columns:
                cell_state = self.cells[row, column].status
                row_rep += f" {cell_reps[cell_state]}"

            rep += row_rep + "\n"
        return rep

    @property
    def label_list(self):
        """Represent the stack as a list of flow-cell labels
        """
        return [cell.label for cell in self.cells.values() if not cell.status == FlowCell.STATUS.OUT_OF_SPEC]


    def mkdirs(self):
        """Create a folder for every flow cell that is not out-of-spec
        """
        for cell in self.cells.values():
            if cell.status == FlowCell.STATUS.OUT_OF_SPEC:
                continue
            cell.mkdir()
