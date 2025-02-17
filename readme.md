# Iceberg Accounting Suite


#### Running from code (Linux):
Running this program from code requires Python 3. Please follow the installation instructions here: https://www.python.org/downloads/

Once you have Python 3 installed, open a terminal and navigate to the Iceberg folder. Enter the following commands to create a virtual environment and run from code:

1. Create a virtual environment in the folder in a hidden subfolder called ".venv".
   
    > python3 -m venv .venv

2. Activate the virtual environment in the terminal:
   
    > source .venv/bin/activate

3. Install all prerequisites in the virtual environment you created:
    > pip install -r requirements.txt

4. Launch Iceberg:
    > python3 iceberg.py


The Graphical User Interface (GUI) will pop up showing the Dashboard or the PySimpleGUI license menu.

Subsequent startups:

1. Open a terminal and navigate to the Iceberg folder.
   
2. Activate the virtual environment:

    > source .venv/bin/activate

3. Launch Iceberg:

    > python3 iceberg.py