# PowerBIData
This is the powerbi RAP process folder for PROMS. It includes everything needed to produce the excel sheet that feeds the PROMS PowerBI Dashboard.

## Set up
1. Download git from the software center (if it does not appear raise a resolveIT)
2. In your Command Prompt App, navigate to the folder where you want to keep the score comparison tool (if you do not know how to do this, look at this website: https://www.lifewire.com/change-directories-in-command-prompt-5185508)
3. Copy the link for this repository from gitlab and type `git clone {URL}` in your command prompt.
4. Now when you navigate to that folder, the Powerbidata folder should appear.
5. If you do not have Visual Studio Code (or another python compiler) installed, download it from the software center and request a python installation from ResolveIT. Do not go on to step 6 before getting this.
6. Go into the commandPrompt app and type the following commands pressing enter between each line: 
```
python -m pip install --user numpy
python -m pip install openpyxl
python -m pip install pandas
python -m pip install pyodbc
```
7. Open the whole folder in Visual Studio by opening visual studio, clicking 'File' then clicking 'Open Folder...' and selecting the score comparison tool folder. 

## Running the Code 
In order to set the variables (dates, tables etc.) needed for the new publication, go into the `config.py` file and change the variables to the ones appropriate for the current publication. This is the only thing that should need changing if nothing about the fundamental aspects of the PowerBI dashboard/file is changing (e.g. no tables or plots are changing).

In order to produce the PowerBI excel file, edit these variables and then run the file by clicking the 'play' button arrow in the top right of Visual Studio Code (if using another program google how to make a code run in that program if you don't know how). 

When running this pipeline, you may get some user warnings such as:  `UserWarning: pandas only supports SQLAlchemy connectable (engine/connection) or database string URI or sqlite3 DBAPI2 connection. Other DBAPI2 objects are not tested. Please consider using SQLAlchemy.` This will not affect how well the program runs and you can ignore it.

# Making Future Changes to the Process
## SQL Queries
 The SQL details are kept in the utils folder in the `queries.py` file, if you want to edit or add more SQL queries, please add them here.

## Connection to the Database
Any time you want to connect to the database for a new query, use the `connection` function that is kept in the utils folder in the `connection.py` file.  

## Requirements.txt
The `requirements.txt` file includes the packages and their versions that are used in this process, you need these installed in order to be able to run this process. To install new packages use `pip install package_name` in the command prompt/terminal.