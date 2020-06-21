# cam-flow
Simple UI for organizing the testing of a stack of flow-cells.

![Demo Animation](assets/stack-editing.gif?raw=true)

Writing hardcoded paths is error-prone. This gui helps make paths and folders, so the are the same every single time. The gui can also prepare the data from each flowcell subfolder as a HTTP payload (watch the terminal while pressing ctrl-W).

## Installation

Make a conda env with dependencies:
```
 > $ conda create --name cam-flow python=3.8
 > $ conda activate cam-flow
 (cam-flow) > $ conda install -c conda-forge kivy pyperclip git
```

Get the python package:
```
 (cam-flow) > $ cd /path/to/folder/where/you/want/package
 (cam-flow) > $ git clone https://github.com/julietKiloRomeo/cam-flow.git
 (cam-flow) > $ cd cam-flow
 (cam-flow) > $ pip install .
```

## Running the GUI

Launch an anaconda powershell (Press windows-key, write anac, select "Anaconda Powershell").
```
 > $ cd /path/to/folder/where/you/want/to/put/stackfiles
 > $ conda activate cam-flow
 (cam-flow) > $ cam-flow
```
![Screenshot](assets/screenshot.png?raw=true)

Start by entering the name of the stack. Click the mouse inside the text field in the top left. Enter the name of the stack and press enter.

Navigate the flow-cell matrix using the arrow keys or the mouse. Mark a flow-cell as out-of-spec with the TAB key.

Press ctrl-P to save a list of labels to the stack-folder (/folder-where-you-started-the-gui/stackname/labels.txt).

Get a path to the top/bottom/other image copied to the clipboard by pressing the corresponding button. The folder will be created if it is not already present. The checkbox cannot be toggled - it will fill out automatically when an image is saved to the correct path.

The 5 questions can be clicked with a mouse (and the answer is immediately saved to a json file in the flow-cell subfolder) or you can toggle them by pressing keys 1-5.

