"""


"""
import npyscreen
import psycopg2

from .db import get_conn, get_puzzle


# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application

class MyTestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", MainForm())

# This form class defines the display that will be presented to the user.

class PuzzleCell(npyscreen.Textfield):

    def display_value(self, value):
        return value


class PuzzleWidget(npyscreen.SimpleGrid):
    _contained_widgets = PuzzleCell 




class MainForm(npyscreen.Form):
    def create(self):
        gen_puzzle = False
        try:
            cursor = get_conn().cursor()
        except psycopg2.ProgrammingError:
            gen_puzzle = True
        puzzle = get_puzzle(cursor)
        self.add(npyscreen.TitleText, name="Text:", value= "Hellow World!" )
        self.add(PuzzleWidget, name="Grid", columns=9, values=puzzle)

    def afterEditing(self):
        self.parentApp.setNextForm(None)


def client():
    TA = MyTestApp()
    TA.run()

if __name__ == "__main__":
    client()