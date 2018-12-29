# Author - Kelly Vo August 16, 2018
import xlrd
import sqlite3
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

# ImportSow function imports the SOW into the database
def importSow():
    # Asks the user for file and opens the workbook and defines the worksheet
    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename()
    book = xlrd.open_workbook(file)
    sheet = book.sheet_by_index(0)
    root.destroy()

    # Establish a sqlite connection
    database = sqlite3.connect(
        'Q:\ACE_&_Business_Excellence\PICA\Co-Op Projects\Kelly Folder\Matrix\matrix.sqlite')  # declare and connect to the sqlite database

    # Get the cursor, which is used to traverse the database, line by line
    cursor = database.cursor()

    # Below comments are to clear the database of all tables
    # cursor.execute('''DROP TABLE IF EXISTS tblSow;''')
    # cursor.execute('''DROP TABLE IF EXISTS tblSowTask;''')
    # cursor.execute('''DROP TABLE IF EXISTS tblSowTaskDel;''')

    # Creates the tables if they don't already exist
    # Creates tblSow
    cursor.execute('''CREATE TABLE IF NOT EXISTS tblSow (
      SowID integer primary key,
      SowNumber varchar,
      SowTitle varchar,
      SowRev integer,
      SowStart varchar
    );''')

    # Creates tblSowTask
    cursor.execute('''CREATE TABLE IF NOT EXISTS tblSowTask(
      SowTaskID integer primary key,
      TaskID integer NOT NULL,
      SowID integer REFERENCES tblSow,
      TaskName varchar,
      TaskEnd varchar
    );''')

    # Creates the tblSowTaskDel if it doesn't already exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS tblSowTaskDel(
      DelID integer primary key,
      SowTaskID integer REFERENCES tblSowTask,
      DelName varchar, 
      DelQTY integer,
      DelQTYDone integer DEFAULT 0,
      DelDue varchar,
      DelResponse varchar,
      DelComments varchar,
      PersonSubmit varchar,
      DelDateDone varchar
    );''')

    # Gets all the SowIDs from tblSow
    cursor.execute('''SELECT SowID FROM tblSow;''')
    sowID = cursor.fetchall()
    if len(sowID) == 0:
        SOWID = 1
    else:
        SOWID = len(sowID) + 1

    # Gets all the SowTaskID from tblSowTask
    cursor.execute('''SELECT SoWTaskID FROM tblSowTask;''')
    sowTaskId = cursor.fetchall()
    if len(sowTaskId) == 0:
        SOWTASKID = 1
    else:
        SOWTASKID = len(sowTaskId) + 1

    # Create a For loop to iterate through each row in the file
    for i in range(1, sheet.nrows):
            cellName = sheet.cell(i, 0).value
            # Gets the SOW number
            if cellName == "SOW Number:":
                customerSowNumber = sheet.cell(i, 3).value
            # Gets the SOW title
            elif cellName == "Title:":
                sowName = sheet.cell(i, 3).value
            # Gets the Revision number
            elif cellName == "Revision #:":
                revNumber = sheet.cell(i, 3).value
            # Gets the SOW start date
            elif cellName == "SOW Start Date":
                sowStartDate = sheet.cell(i, 3).value
                # Inserts into the table tblSow
                cursor.execute('''INSERT INTO tblSow(SowID, SowNumber, SowTitle, SowRev, SowStart) VALUES (?, ?, ?, ?, ?);''', (SOWID, customerSowNumber, sowName, int(revNumber), sowStartDate))
                SOWID += 1
            # Gets the SOW author
            elif cellName == "Author":
                authorName = sheet.cell(i, 5).value
            # Gets the Technical Contact
            elif cellName == "Technical Contact:":
                techName = sheet.cell(i, 5).value
            # Gets the SOW Status
            elif cellName == "Released" or cellName == "Hold":
                sowTaskNumber = sheet.cell(i, 1).value
                sowTask = sheet.cell(i, 2).value
                sowTaskEndDate = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(sheet.cell(i, 6).value) - 2)
                sowTaskEndDate = str(datetime.date(sowTaskEndDate).strftime("%m-%d-%Y"))
                sowTaskDes = sheet.cell(i, 4).value
                # Gets SOW ID from tblSOW that match the SOW Number
                cursor.execute('''SELECT SowID FROM tblSow WHERE SowNumber = ? ;''', (customerSowNumber,))
                sowID = cursor.fetchall()
                # Inserts into the table tblSowTask
                cursor.execute('''INSERT INTO tblSowTask(SowTaskID, SowID, TaskID, TaskName, TaskEnd) VALUES (?,?,?,?,?);''',(SOWTASKID, sowID[0][0], int(sowTaskNumber), sowTask, sowTaskEndDate))
                SOWTASKID += 1
                j = 1
                while sheet.cell(i + j, 3).value != "":
                    sowDel = sheet.cell(i + j, 3).value
                    sowDelDes = sheet.cell(i + j, 4).value
                    sowDelQTY = sheet.cell(i + j, 5).value
                    sowDelEnd = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(sheet.cell(i + j, 6).value) - 2)
                    sowDelEnd = str(datetime.date(sowDelEnd).strftime("%m-%d-%Y"))
                    # Gets SOW Task ID that matched the Task ID and the SOW ID
                    cursor.execute('''SELECT SoWTaskID FROM tblSowTask WHERE TaskID = ? AND SoWID = ? ;''', (int(sowTaskNumber), int(sowID[0][0])))
                    sowTaskId = cursor.fetchall()
                    # Inserts into the table tblSowTaskDel
                    cursor.execute('''INSERT INTO tblSowTaskDel(SoWTaskID, DelName, DelQTY, DelDue) VALUES (?, ?, ?, ?);''', (sowTaskId[0][0], sowDel, sowDelQTY, sowDelEnd))
                    j = j + 1
    # Close the cursor
    cursor.close()

    # Commit the transaction
    database.commit()

    # Close the database connection
    database.close()

# Main function runs the program by importing the sow
def main():
    importSow()

if __name__ == '__main__':
    main()
