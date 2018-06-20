from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from Settings import settings as gl
import sqlite3
from kivy.graphics import Ellipse
from kivy.app import App
from Settings.settings_kv import TimeCounter
import datetime
from kivy.clock import Clock
from Target_window.goals_plan import display_place_plan_goals


def sleep_mode_display():
    bedtime = App.get_running_app().root.ids.application_screen.ids._target_window.ids._sleep_mode.ids._bedtime
    wakeup = App.get_running_app().root.ids.application_screen.ids._target_window.ids._sleep_mode.ids._wakeup

    hour_bedtime = bedtime.ids._hour
    minute_bedtime = bedtime.ids._minute
    hour_wakeup = wakeup.ids._hour
    minute_wakeup = wakeup.ids._minute
    conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("select bedtime, wakeup from sleeptime where user_id = ?", (gl.USER_ID,))
    result = cursor.fetchall()
    conn.close()
    def output(time):
        return '0' + str(time) if time<10 else str(time)
    hour_bedtime.text = output(result[0][0].hour)
    minute_bedtime.text = output(result[0][0].minute)
    minute_wakeup.text = output(result[0][1].minute)
    hour_wakeup.text = output(result[0][1].hour)
    sleep_mode_update_graph()

def sleep_mode_update_graph():
    grapha = App.get_running_app().root.ids.application_screen.ids._target_window.ids._sleep_mode.ids._graph
    whole_time = App.get_running_app().root.ids.application_screen.ids._target_window.ids._sleep_mode.ids._whole_sleep_time
    conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("select bedtime, wakeup from sleeptime where user_id = ?", (gl.USER_ID,))
    result = cursor.fetchall()
    conn.close()
    zero = datetime.datetime(2018, 1, 1, 0, 0)
    whole_time.text = (zero+(result[0][1]-result[0][0])).strftime("%H:%M")
    draw_graph(grapha, result[0][0].hour, result[0][1].minute,result[0][1].hour, result[0][1].minute )

def draw_graph(obj, hour_bed, min_bed, hour_wakeup, min_wakeup):
    def get_time_start(hour, min):
        return (hour-12)*30+min*0.5-360 if hour>12 else (hour)*30+min*0.5
    def get_time_end(hour, min):
        return (hour)*30+min*0.5
    with obj.canvas:
        Ellipse(angle_start=0, angle_end=360, pos=(0, 0), size=obj.size,source='Settings/images/sleep_mode/sleep_bottom.png')
        Ellipse(angle_start=get_time_start(hour_bed,min_bed), angle_end=get_time_end(hour_wakeup,min_wakeup), pos=(0,0), size=obj.size, source='Settings/images/sleep_mode/sleep_top.png')


class SleepMode(Screen):
    bedtime = ObjectProperty(None)
    graph = ObjectProperty(None)
    wakeup = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._update_graph)

    def _update_graph(self, dt):
        arrows = ['_up_hour','_up_minute','_down_hour', '_down_minute']
        for i,v in enumerate(arrows):
            self.ids._bedtime.ids[v].bind(on_press = self.my_callback)
            self.ids._wakeup.ids[v].bind(on_press=self.my_callback)

    def my_callback(self, *args):
        hour_bedtime = int(self.bedtime.ids._hour.text)
        minute_bedtime = int(self.bedtime.ids._minute.text)
        hour_wakeup = int(self.wakeup.ids._hour.text)
        minute_wakeup = int(self.wakeup.ids._minute.text)
        draw_graph(self.graph, hour_bedtime,minute_bedtime,hour_wakeup,minute_wakeup)
        self.ids._whole_sleep_time.text = (datetime.datetime(2018,1,1,0,0)+(datetime.datetime(2018,1,1,hour_wakeup, minute_wakeup)-datetime.datetime(2018,1,1,hour_bedtime, minute_bedtime))).strftime("%H:%M")



    def save_time(self):
        hour_bedtime = int(self.bedtime.ids._hour.text)
        minute_bedtime = int(self.bedtime.ids._minute.text)
        hour_wakeup = int(self.wakeup.ids._hour.text)
        minute_wakeup = int(self.wakeup.ids._minute.text)
        bedtime=datetime.datetime(2018,1,1,hour_bedtime, minute_bedtime)
        wakeup = datetime.datetime(2018, 1, 1, hour_wakeup, minute_wakeup)
        conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("update sleeptime set bedtime=?, wakeup=? where user_id = ?", (bedtime, wakeup, gl.USER_ID,))
        conn.commit()
        conn.close()
        sleep_mode_display()
        display_place_plan_goals()

    def update_time(self):
        sleep_mode_display()
class TimeCounterGraph(TimeCounter):
    pass