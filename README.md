# CS5110-Final-Project

## Environment

### Setting up
To run our project, set up a virtual python environment with `python -m venv .venv`, then activate it by typing `source .venv/Scripts/activate` or `source .venv/Scripts/bin/activate` in a UNIX environment. Finally, install the required dependencies into your new virtual environment with `pip install -r requirements.txt`.

### Running the project
With that, you can run the main file using `python3 src/main.py`.
You will see a window pop up and ... `TODO`

### Breaking down
Finally, deactivate your new environment so it doesn't bother you later by simply typing `deactivate`.

## File Structure map
```
 .
 ├─ src
 │ ├─ algorithms
 │ │  ├─ test_<algorithm>.py  # A unittest class
 │ │  ├─ <algorithm>.py       # The bare algorithm implementation
 │ │  ├─ <algorithm>.ipynb    # A Jupyter notebook containing the animated visualization of the algorithm
 │ │  ├─ <algorithm>_animation.gif  # Aforementioned animated visualization saved as a .gif file
 │ │  └─ <algorithm>_time_complexity.png  # A simple chart comparing expected runtime against measured runtime
 │ ├─ helpers
 │ │  └─ heap.py  # A simple implementation of a Fibonacci minheap PriorityQueue which was not used
 │ ├─ ui
 │ │  ├─ runners
 │ │  │  └─  ...  # Files used to run the algorithms within the GUI
 │ │  ├─ ...
 │ │  └─ ...      # Relatively self-explanatory files used to build the GUI
 │ └─ main.py     # The main file to run in order to use the GUI
 ├─ .gitignore
 ├─ README.md
 ├─ requirements.txt
 └─ WriteUp.pdf
```
