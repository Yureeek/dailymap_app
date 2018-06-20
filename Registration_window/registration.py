from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
import json
import sqlite3
from kivy.app import App
import Settings.settings as gl  #global application variable
import datetime

#to update the information when you login to the system
from NavigationBar.navigationbar import display_right_corner_username
from Target_window.sleep_mode import sleep_mode_display
from Target_window.goals_creation import display_place_goals
from Target_window.goals_plan import display_place_plan_goals
from Schedule_window.schedule import display_schedule
from Schedule_window.schedule import display_categories

class EntryScreen(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    win_screen = ObjectProperty(None)
    error_lbl = ObjectProperty(None)

    def enter_user(self):
        if not self.username.text:
            self.error_lbl.text = 'Username field is empty'
            return 0
        if not self.password.text:
            self.error_lbl.text = 'Password field is empty'
            return 0

        conn = sqlite3.connect('dailymap.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (self.username.text, self.password.text))
        gl.USER_ID = cursor.fetchall()
        conn.close()

        if not gl.USER_ID:
            self.error_lbl.text = 'Incorrect username or password'
            return 0
        #release the variable from the list and the tuple
        gl.USER_ID = gl.USER_ID[0][0]  # USER_ID = [(ID,)]  -> (ID,) -> ID

    #********** to update the information when you login to the system   **********
        self.win_screen.current = 'application_window' #change screen
        display_right_corner_username()# shows in the right top corner after the entrance
        sleep_mode_display() #show your time sleep in sleep_window
        display_place_goals() #show your goals in thw goals_creation window
        display_place_plan_goals() #show yout week plan goals

        display_schedule()
        display_categories()
    # ********** to update the information when you login to the system   **********




class RegistrationScreen(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    confirm_password = ObjectProperty(None)
    win_screen = ObjectProperty(None)
    error_lbl = ObjectProperty(None)

    def register_user(self):
        if not self.username.text:
            self.error_lbl.text = 'Username field is empty'
            return 0
        if not self.password.text:
            self.error_lbl.text = 'Password field is empty'
            return 0
        if not self.confirm_password.text:
            self.error_lbl.text = 'Confirm password field is empty'
            return 0
        if len(self.username.text)>25:
            self.error_lbl.text = 'The username is too long'
            return 0
        if gl.check_input(self.username.text) or gl.check_input(self.password.text):
            self.error_lbl.text = 'Invalid characters entered'
            return 0
        if self.password.text != self.confirm_password.text:
            self.error_lbl.text = "Passwords don't match"
            return 0


        conn = sqlite3.connect('dailymap.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", [(self.username.text)])  # проверяем есть ли уже пользователь с таким именем
        res = cursor.fetchall()
        conn.close()
        if res:
            self.error_lbl.text = 'This name is used'
            return 0
        #add user to the database
        conn = sqlite3.connect('dailymap.db')
        cursor = conn.cursor()
        cursor.executemany("INSERT INTO users (username, password, icon) VALUES (?, ?, ?)", [(self.username.text, self.password.text, 'user.png')])
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (self.username.text, self.password.text))
        gl.USER_ID = cursor.fetchall()
        gl.USER_ID = gl.USER_ID[0][0] # USER_ID = [(ID,)]  -> (ID,) ->ID
        #*** update all tables
        cursor.executemany("INSERT INTO sleeptime (user_id, bedtime, wakeup) VALUES (?, ?, ?)",[(gl.USER_ID, datetime.datetime(2018,1,1,23,0), datetime.datetime(2018,1,1,7,0))])
        conn.commit()
        conn.close()
    # ********** to update the information when you login to the system   **********
        self.win_screen.current = 'application_window'  # change screen
        display_right_corner_username()  # shows in the right top corner after the entrance
        sleep_mode_display()  # show your time sleep in sleep_window
        display_place_goals()  # show your goals in thw goals_creation window
        display_place_plan_goals()  # show yout week plan goals
        display_schedule()
    # ********** to update the information when you login to the system   **********




























'''
регистрация с помощью файлов
 def enter_user_files(self):

        simbols = {}
        if not self.username.text:
            self.error_lbl.text = 'Username field is empty'
            return 0
        if not self.password.text:
            self.error_lbl.text = 'Password field is empty'
            return 0


        with open('Registration_window/users.json') as file:
            usr = json.load(file)

        for i in range(len(usr)):
            if self.username.text == usr[i]['username'] and self.password.text == usr[i]['password']:
                self.error_lbl.text = 'This is right data'
                self.win_screen.current = 'report_window'
                return True
        self.error_lbl.text = 'Incorrect username or password'

 def register_user_file(self):
        if not self.username.text:
            self.error_lbl.text = 'Username field is empty'
            return 0
        if not self.password.text:
            self.error_lbl.text = 'Password field is empty'
            return 0
        if not self.confirm_password.text:
            self.error_lbl.text = 'Confirm password field is empty'
            return 0

        if self.password.text != self.confirm_password.text:
            self.error_lbl.text = "Passwords don't match"
            return 0

        with open('Registration_window/users.json') as file:      #открываем файл
            usr = json.load(file)                          #получаем список кортежей

        for i in range(len(usr)):                          #проверяем есть ли уже пользователь с таким именем

            if self.username.text == usr[i]['username']:
                self.error_lbl.text = 'This name is used'
                return 0


        usr.append({                                       #добавляем нового пользователя в список кортежей
                'id': len(usr),
                'username': self.username.text,
                'password': self.password.text,
            })

        with open('Registration_window/users.json', 'w') as file: #открываем файл и переписываем заного всю БД вместе с новым пользователем
            json.dump(usr, file, indent=2)
        self.win_screen.current = 'report_window'           #переключаем скрин

        #self.parent.parent.parent.parent.parent.win_screen.current = 'application_window'
        #self.root.win_screen.current = 'application_window'
        #print(self.parent.parent.parent.parent.manager)
        #self.parent.parent.parent.parent.manager.current = 'application_window'
'''