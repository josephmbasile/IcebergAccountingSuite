# Iceberg Accounting Suite

IceBerg Account Suite is intended to be a full-featured bookkeeping application for households, bookkeepers, CPAs, and Tax Professionals to use when tracking financial records.

## Version
Version 1.02 (Calving Crutons)

## Current Features
Currently, the software is capable of running encrypted bookkeeping databases with physical keys. The GUI can be used to journal transactions against a set of accounts using double-entry bookkeeping. Currently, vendor tracking is enabled, but Customer tracking, Invoicing, and Inventory have yet to be created, making the software useful to researchers, casual users, and households only. 



## Installation (Linux)

This software requires Python3 to run. Please follow the instructions here: https://www.python.org/downloads/

Download the entire respository from GitHub. Unzip the repository to your desired storage location. 

1. Create a virtual environment in the folder in a hidden subfolder called ".venv".
   
    > python3 -m venv .venv

2. Activate the virtual environment in the terminal:
   
    > source .venv/bin/activate

3. Install all prerequisites in the virtual environment you created:
    > pip install -r requirements.txt

4. If there were no errors, check the progress bar below to see how the installation is going:

|----------------------------------------------------------->|100% Complete

Congratulations! Iceberg Accounting Suite has been installed on your system.


## Opening the Software

#### Running from code (recommended):
These instructions assume you've already installed the software according to the instructions in this document. If you already have your virtual environment active you can skip to step 3.

1. Navigate to your Iceberg folder.

2. Activate the virtual environment in the terminal:
   
    > source .venv/bin/activate

3. Launch Iceberg Accounting Suite:
    > python3 iceberg.py


The Graphical User Interface (GUI) will pop up showing the Dashboard.

### Windows

Build an executable using pyinstaller or run from code. Please post your solution to a Git branch.

### MacOS

Build an executable using pyinstaller or run from code. Please post your solution to a Git branch.


