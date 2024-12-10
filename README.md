# CS5110-Final-Project

## Environment

### Setting up
To run our project, set up a virtual python environment with `python -m venv .venv`, then activate it by typing `source .venv/Scripts/activate` or `source .venv/Scripts/bin/activate` in a UNIX environment. Finally, install the required dependencies into your new virtual environment with `pip install -r requirements.txt`.

### Running the GUI
With that, you can run the main file using `python3 src/main.py`.
You will see a window pop up and you are free to build and manipulate your graph!  

#### GUI Functionality
- Run an Algorithm
  - Clicking this button opens a popup window which prompts you with one of our four implemented algorithms to be run on your current graph
- Graph Generation
  - Clicking this button opens a popup window which prompts you to click and drag options for building your graph
  - You must specify the number of nodes in your newly generated graph in the appropriate text box
- Three 'manual' manipulation modes
  - Select
    - Left click and drag an existing vertex to displace it
  - Vertices
    - Left click an empty space to create a Vertex with an auto-generated label
    - Right click a vertex to remove it
  - Edges
    - Left click an initial node and a link node to create an edge between the two
    - Right click an existing edge to remove it
- Clear the graph
  - With just one click of this button, you can wipe your canvas clean and start anew!
- Edge Weights
  - Edge weights can be specified by adding an integer value to the text box before creating an edge
  - Edge weights can be toggled on/off for the entire graph by clicking the checkbox
- Graph Directed-ness
  - You can toggle whether the graph is directed or not by clicking the appropriate checkbox

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
 │ │  └─ heap.py  # A simple implementation of a Binary minheap PriorityQueue which was not used
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
