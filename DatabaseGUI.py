# Created by Aditya Gopinath and Kelly Vo September 14, 2018

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
import subprocess
import sqlite3
import datetime
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

# Sets window size
Window.size = (1200, 700)
# Sets the window position
Window.left = 40
# database is the database
database = sqlite3.connect('Q:\ACE_&_Business_Excellence\PICA\Co-Op Projects\Kelly Folder\Matrix\matrix.sqlite') #declare and connect to the sqlite database
# cursor is used to traverse the database, line by line
cursor = database.cursor()
# Loads the Kivy file which contains all the GUI elements
Builder.load_file('gui.kv')

# Below comments are to clear the database of all tables
# cursor.execute('''DROP TABLE IF EXISTS tblSow;''')
# cursor.execute('''DROP TABLE IF EXISTS tblSowTask;''')
# cursor.execute('''DROP TABLE IF EXISTS tblSowTaskDel;''')

# Creates the tblSow table if it doesn't already exist
cursor.execute('''CREATE TABLE IF NOT EXISTS tblSow (
  SowID integer primary key,
  SowNumber varchar,
  SowTitle varchar,
  SowRev integer,
  SowStart varchar
);''')

# Creates the tblSowTask table if it doesn't already exist
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

# extends the App class (used to initialize Kivy apps)
class MetricsTrackerApp(App):

    # The title seen on the top left of a window
    title = 'Metrics Tracker'

    def build(self):
        # Returns the screen to display the GUI
        return sm

    def importSOW(self):
        # Calls the ImportSow.py file
        subprocess.Popen("ImportSow.py", shell=True)

    # Fetches the list of sows from the database
    def showTblSow(self):
        # executes this SQL command
        cursor.execute('''SELECT tblSow.SowNumber FROM tblSow;''')
        # assigns the fetched sows of the SQL command to a list
        sowID = cursor.fetchall()
        # returns the assigned list
        return sowID

    # Fetches the list of tasks from the database. (taskName is provided on click)
    def showTasks(self,taskName):
        # executes this SQL command
        cursor.execute('''SELECT tblSowTask.TaskName
				FROM tblSow INNER JOIN tblSowTask ON tblSow.SoWID = tblSowTask.SoWID
				WHERE ((tblSow.SoWNumber)=?)''', (str(taskName),))
        # assigns the fetched tasks of the SQL command to a list
        taskID = cursor.fetchall()
        # returns the assigned list
        return taskID

    # Gets the deliverable names for a specific task name and sow name
    def showDel(self, taskName, sowName):
        # Executes this SQL command
        cursor.execute('''SELECT tblSowTaskDel.DelName
				FROM tblSowTask INNER JOIN tblSowTaskDel ON tblSowTask.SoWTaskID = tblSowTaskDel.SoWTaskID
				WHERE  (((tblSowTask.TaskName)=?)) AND tblSowTask.SoWID = (SELECT tblSow.SoWID 
				FROM tblSow WHERE (((tblSow.SoWNumber)=?)))''', (str(taskName), str(sowName),))
        delID = cursor.fetchall()
        # Returns the assigned list
        return delID

    # Gets the total QTY for a specific deliverable
    def showTotalQTY(self, task, delName):
        # Executes this SQL command
        cursor.execute('''SELECT tblSowTaskDel.DelQTY
			FROM tblSowTask INNER JOIN tblSowTaskDel ON tblSowTask.SoWTaskID = tblSowTaskDel.SoWTaskID
			WHERE (((tblSowTask.TaskName)=?) And (((tblSowTaskDel.DelName)=?)))''', (str(task), str(delName),))
        qty = cursor.fetchall()
        # Returns the assigned list
        return qty

    # Gets the QTY finished for a specific deliverable
    def showQTY(self, task, delName):
        # Executes this SQL command
        cursor.execute('''SELECT tblSowTaskDel.DelQTYDone
			FROM tblSowTask INNER JOIN tblSowTaskDel ON tblSowTask.SoWTaskID = tblSowTaskDel.SoWTaskID
			WHERE (((tblSowTask.TaskName)=?) And (((tblSowTaskDel.DelName)=?)))''', (str(task), str(delName),))
        qty = cursor.fetchall()
        # Returns the assigned list
        return qty

    # Used to create X buttons on click (X = length of task names list)
    def getLen(self, taskName):
        # Object of this class to access functions
        taskObj = MetricsTrackerApp
        # Returns the length of task names list.
        return len(taskObj.showTasks(MetricsTrackerApp, taskName))

#Declare all screens
class MainMenu(Screen):
    pass

class Burndown(Screen):
    # appObj is the MetricsTrackerApp
    appObj = MetricsTrackerApp
    # value gets all the SOW names in the database
    sows = appObj.showTblSow(MetricsTrackerApp)
    # v is a list of all the SOW names in the database
    v = [str(t[0]) for t in sows]

    # makeSpin sets the task spinner values with all the tasks for the specific SOW
    def makeSpin(self, sow):
        # appObj is the MetricsTrackerApp
        appObj = MetricsTrackerApp
        # tasks gets all the task names in the database
        tasks = appObj.showTasks(MetricsTrackerApp, sow)
        # t is a list of all the tasks names in the database
        t = [str(t[0]) for t in tasks]
        # Sets spinnerTask's values to t
        self.ids.spinnerTask.values = t

    # makeGrid adds values to the grid layout of all the data for the task chosen
    def makeGrid(self, name, spinnerText):
        # appObj is the MetricsTrackerApp
        appObj = MetricsTrackerApp
        # dels gets all the deliverable names in the database
        dels = appObj.showDel(MetricsTrackerApp, name, spinnerText)

        # Deletes the values in the grid layout if there are any
        self.ids.grid.clear_widgets()

        # Loops through each deliverable and adds the deliverable name, QTY done, Total QTY and the Percentage of the
        # deliverable done
        for i in range(len(dels)):
            # Gets the deliverable name
            delName = str(dels[i][0]).strip()
            # Creates the Deliverable label
            DelLabel = Label(text=str(delName),pos_hint={'x':.3, 'y':((1-(i/10))-.5)}, size_hint=(.15, .1))
            # Gets the total QTY for the deliverable
            totalQty = str(appObj.showTotalQTY(MetricsTrackerApp, name, dels[i][0])[0][0]).strip()
            # Gets the QTY done for the deliverable
            qtyDone = str(appObj.showQTY(MetricsTrackerApp, name, dels[i][0])[0][0]).strip()
            # Creates the QTY label
            QTYlabel = Label(text=str(qtyDone) + " / " + str(totalQty), pos_hint={'x':.52, 'y':((1-(i/10))-.5)}, size_hint=(.15, .1))
            # Calculates the percentage
            percent = ((int(qtyDone) / int(totalQty)) * 100)
            # Creates the Percent label
            PercentLabel = Label(text=str(percent) + "%", pos_hint={'x':.765, 'y':((1-(i/10))-.5)}, size_hint=(.15, .1))

            # Adds the Deliverable label to the grid layout
            self.ids.grid.add_widget(DelLabel)
            # Adds the QTY label to the grid layout
            self.ids.grid.add_widget(QTYlabel)
            # Adds the Percent label to the grid layout
            self.ids.grid.add_widget(PercentLabel)

    # Clears the grid layout of any widgets
    def Clear(self):
        self.ids.grid.clear_widgets()

class Executioner(Screen):
    # appObj is the MetricsTrackerApp
    appObj = MetricsTrackerApp
    # sows gets all the SOW names in the database
    sows = appObj.showTblSow(MetricsTrackerApp)
    # v is a list of  all the SOW names in the database
    v = [str(t[0]) for t in sows]

    # makeSpin sets the task spinner values with all the tasks for the specific SOW
    def makeSpin(self, sow):
        # appObj is the MetricsTrackerApp
        appObj = MetricsTrackerApp
        # tasks gets all the task names in the database
        tasks = appObj.showTasks(MetricsTrackerApp, sow)
        # t is a list of all the tasks names in the database
        t = [str(t[0]) for t in tasks]
        # Sets spinnerTask's values to t
        self.ids.spinnerTask.values = t

    # makeGrid adds values to the grid layout of all the data for the task chosen
    def makeGrid(self, name, spinnerText):
        # Makes sure the user selected a task
        if name != 'Task':
            # appObj is the MetricsTrackerApp
            appObj = MetricsTrackerApp
            # dels gets all the deliverable names in the database
            dels = appObj.showDel(MetricsTrackerApp, name, spinnerText)

            # Deletes the values in the grid layout if there are any
            self.ids.grid.clear_widgets()

            # Loops through each deliverable and adds the deliverable name, current date, spinner for the number of QTY
            # for each deliverable, spinner containing all the responses for the deliverable, text input for the
            # person's name, and text input for any additional comments
            for i in range(len(dels)):
                # Gets the deliverable name
                delName = str(dels[i][0]).strip()
                # Creates the Deliverable label
                DelLabel = Label(id=str("Label" + str(i)), text=str(delName), size_hint=(.15, .1),
                             pos_hint={'x': .165, 'y': ((1 - (i / 10)) - .5)})
                # Gets the total QTY for the deliverable
                totalQty = str(appObj.showTotalQTY(MetricsTrackerApp, name, dels[i][0])[0][0]).strip()
                # qty is a list of all the numbers from 0 to the total QTY
                qty = [str(t) for t in range(0, int(totalQty) + 1)]
                # response is a list of all the responses for the responseSpinner
                response = ["Late Customer Input", "Network Issues", "Infrastructure Issues", "Other"]
                # Creates the QTY spinner
                QTYSpinner = Spinner(id=str("QTY" + str(i)), text="", values=qty, size_hint=(.05, .1),
                                   pos_hint={'x': .32, 'y': ((1 - (i / 10)) - .5)})
                # Creates the Response spinner
                ResponseSpinner = Spinner(id=str("Response" + str(i)), text="", values=response, size_hint=(.15, .1),
                                   pos_hint = {'x': .39, 'y': ((1 - (i / 10)) - .5)})
                # Finds the current date
                now = datetime.datetime.now()
                # Creates the Date label
                DateLabel = Label(id=str("Date" + str(i)), text=now.strftime("%m-%d-%Y"), size_hint=(.15, .1),
                             pos_hint={'x': .52, 'y': ((1 - (i / 10)) - .5)})
                # Creates the person text input
                PersonInput = TextInput(id=str("Person" + str(i)), text="", size_hint=(.15, .08),
                                   pos_hint={'x': .65, 'y': ((1 - (i / 10)) - .49)})
                # Creates the comments text input
                CommentsInput = TextInput(id=str("Comments" + str(i)), text="", size_hint=(.15, None),
                                     pos_hint={'x': .81, 'y': ((1 - (i / 10)) - .5)})

                # Adds the Deliverable label to the grid layout
                self.ids.grid.add_widget(DelLabel)
                # Adds the Date label to the grid layout
                self.ids.grid.add_widget(DateLabel)
                # Adds the QTY spinner to the grid layout
                self.ids.grid.add_widget(QTYSpinner)
                # Adds the Response Spinner to the grid layout
                self.ids.grid.add_widget(ResponseSpinner)
                # Adds the Person text input to the grid layout
                self.ids.grid.add_widget(PersonInput)
                # Adds the Comments text input to the grid layout
                self.ids.grid.add_widget(CommentsInput)

    # Clears the grid layout of any widgets
    def Clear(self):
        self.ids.grid.clear_widgets()

    # Updates the database when the user clicks on submit
    def UpdateDatabase(self, num):
        # Loops through the number of deliverables
        for x in range(0, num):
            # Loops through the widgets in the grid layout
            for i in range(0, len(self.ids.grid.children)):
                # If the last character of the widget id matches x
                if str(x) == str(self.ids.grid.children[i].id)[-1]:
                    # Checks to make sure that if the response is 'Other', then Comments cannot be empty
                    if self.ids.grid.children[i + 2].text == "Other" and self.ids.grid.children[i].text == "":
                        # if so, makes a pop up to warn user
                        box = BoxLayout(orientation='vertical', padding=(10))
                        labl = Label(text="Specify Your Response of 'Other' in the 'Comments' Section for Deliverable: "
                                           + self.ids.grid.children[i + 5].text)
                        box.add_widget(labl)
                        popup = Popup(title='Warning',
                                    content=box,
                                    size_hint=(None, None), size=(650, 100), pos=(0, 0))
                        popup.open()
                        return None
                    # qty is the text value of the QTY spinner
                    qty = self.ids.grid.children[i + 3].text
                    # If the text value of the QTY spinner is empty
                    if self.ids.grid.children[i + 3].text == '':
                        # Make qty 0
                        qty = 0
                    else:
                        # Otherwise, convert the text value into a integer
                        qty = int(qty)
                    # Checks to make sure that if the qty is greater and the Person text input is empty
                    if qty > 0 and self.ids.grid.children[i + 1].text == '':
                        # if so, makes a pop up to warn user
                        box = BoxLayout(orientation='vertical', padding=(10))
                        labl = Label(text="State the Person that completed the Deliverable: "
                                          + self.ids.grid.children[i + 5].text)
                        box.add_widget(labl)
                        popup = Popup(title='Warning',
                                      content=box,
                                      size_hint=(None, None), size=(500, 100), pos=(0, 0))
                        popup.open()
                        return None
                    # Execute SQL update statement to update the database
                    cursor.execute("UPDATE tblSowTaskDel SET DelResponse =?, DelComments =?, PersonSubmit =?, DelQTYDone =?, DelDateDone =? WHERE DelName =?",
                                   (self.ids.grid.children[i + 2].text,
                                    self.ids.grid.children[i].text,
                                    self.ids.grid.children[i + 1].text,
                                    qty,
                                    self.ids.grid.children[i + 4].text,
                                    self.ids.grid.children[i + 5].text))
                    # Commits the changes to the database
                    database.commit()
                    # Increment x
                    x += 1
        # Creates a pop up to tell the user that the database is updated
        box = BoxLayout(orientation='vertical', padding=(10))
        labl = Label(text="Database Has Been Updated!")
        box.add_widget(labl)
        popup = Popup(title='Finished!',
                      content=box,
                      size_hint=(None, None), size=(500, 100), pos=(0, 0))
        popup.open()
        # Clears the values of all the widgets in the screen
        self.ids.spinnerTask.text = 'Task'
        self.ids.spinnerSow.text = 'Choose a SOW'
        # Clears all the widgets in the grid layout
        self.ids.grid.clear_widgets()


# Create the screen manager, adds the screens to the GUI and name the screens
sm = ScreenManager()
sm.add_widget(MainMenu(name='menu'))
sm.add_widget(Burndown(name='burndownScreen'))
sm.add_widget(Executioner(name='completionScreen'))

# Runs the program
if __name__ == '__main__':
    MetricsTrackerApp().run()
