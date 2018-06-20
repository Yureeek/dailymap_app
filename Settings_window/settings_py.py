from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
import sqlite3
from kivy.app import App
from kivy.properties import ObjectProperty
import Settings.settings as gl
#from NavigationBar.navigationbar import display_right_corner_username

class ExitBtn(Button):
    def exit(self):
        App.get_running_app().root_registration_manager.current = 'registration_window'
        App.get_running_app().root_application_manager.current = 'schedule_window'
    def on_press(self):
        super().on_press()
        self.exit()

class Settings_methods():
    def display_user_data_settings(self):
        username_settings = App.get_running_app().root.ids.application_screen.ids._settings_window.ids._personal_window.ids._username
        password_settings = App.get_running_app().root.ids.application_screen.ids._settings_window.ids._personal_window.ids._password
        email_settings = App.get_running_app().root.ids.application_screen.ids._settings_window.ids._personal_window.ids._email
        '''Update data when you click settings button (navigation.py)'''
        conn = sqlite3.connect('dailymap.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE id=?", (gl.USER_ID,))
        result = cursor.fetchall()
        conn.close()
        username_settings.text = result[0][0]
        email_settings.text = str(result[0][1])
        password_settings.text = ''

class PersonalInformation(Screen, Settings_methods):
    username = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    error_lbl = ObjectProperty(None)
    def update_user_data(self):
        if not self.username.text:
            self.error_lbl.text = 'Username field is empty'
            return 0
        if not self.password.text:
            self.error_lbl.text = 'Password field is empty'
            return 0
        if len(self.username.text)>25:
            self.error_lbl.text = 'The username is too long'
            return 0
        if gl.check_input(self.username.text) or gl.check_input(self.password.text):
            self.error_lbl.text = 'Invalid characters entered'
            return 0

        conn = sqlite3.connect('dailymap.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id=? and password =? ",  (gl.USER_ID, self.password.text))  # проверяем пароль
        res = cursor.fetchall()
        conn.close()
        if not res:
            self.error_lbl.text = 'Invalid password'
            return 0

        conn = sqlite3.connect('dailymap.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, email FROM users WHERE id=?", (gl.USER_ID,))  # проверяем есть ли уже пользователь с таким именем
        res = cursor.fetchall()
        conn.close()
        if res[0][0]==self.username.text and res[0][1]==self.email.text:
            self.error_lbl.text = "You didn't change anything"
            return 0
        elif res[0][0]!=self.username.text and res[0][1]==self.email.text:
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=?", (self.username.text,))  # проверяем есть ли уже пользователь с таким именем
            res = cursor.fetchall()
            conn.close()
            if res:
                self.error_lbl.text = 'This name is used'
                return 0
            # change user data
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("update users set username=? where id =?",(self.username.text, gl.USER_ID))
            conn.commit()
            conn.close()

        elif res[0][0]==self.username.text and res[0][1]!=self.email.text:
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email=?",(self.email.text,))  # проверяем есть ли уже пользователь с таким именем
            res = cursor.fetchall()
            conn.close()
            if res:
                self.error_lbl.text = 'This email is used'
                return 0
            # change user data
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("update users set email=? where id =?",(self.email.text, gl.USER_ID))
            conn.commit()
            conn.close()

        elif res[0][0]!=self.username.text and res[0][1]!=self.email.text:
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username=?",(self.username.text,))  # проверяем есть ли уже пользователь с таким именем
            res = cursor.fetchall()
            conn.close()
            if res:
                self.error_lbl.text = 'This username is used'
                return 0
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email=?", (self.email.text,))  # проверяем есть ли уже пользователь с таким именем
            res = cursor.fetchall()
            conn.close()
            if res:
                self.error_lbl.text = 'This email is used'
                return 0
            # change user data
            conn = sqlite3.connect('dailymap.db')
            cursor = conn.cursor()
            cursor.execute("update users set username=?, email=? where id =?",(self.username.text, self.email.text, gl.USER_ID))
            conn.commit()
            conn.close()

        username_lbl = App.get_running_app().root.ids.application_screen.ids._navigation_bar.ids._username
        username_lbl.text = self.username.text
        username_lbl.width = len(self.username.text) * 10
        self.display_user_data_settings()
        self.error_lbl.text = 'Successfully changed'




