
from kivy.app import App
import sqlite3
from kivy.graphics import Color
import Settings.settings as gl
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from Settings_window.settings_py import Settings_methods

class NavigationBar(BoxLayout, Settings_methods):
    target_btn = ObjectProperty(None)
    schedule_btn = ObjectProperty(None)
    dashboard_btn = ObjectProperty(None)
    settings_btn = ObjectProperty(None)




def display_right_corner_username():
    username_lbl = App.get_running_app().root.ids.application_screen.ids._navigation_bar.ids._username
    conn = sqlite3.connect('dailymap.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, email FROM users WHERE id=?", (gl.USER_ID,))
    result = cursor.fetchall()
    conn.close()
    username_lbl.text = result[0][0]
    username_lbl.width = 10+len(username_lbl.text)*10



