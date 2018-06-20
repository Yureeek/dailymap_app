from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from Settings import settings as gl
from kivy.uix.togglebutton import ToggleButton
import sqlite3
from kivy.graphics import Rectangle
from kivy.app import App
from kivy.clock import Clock
import datetime
from Settings.settings_kv import TimeCounter
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

def select_from_db(query, *args, db='dailymap.db'):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute(query, (*args,))
    result = cursor.fetchall()
    conn.close()
    return result

goals_id_list=[]
week_begin=None
def display_place_plan_goals(date_start = datetime.date(datetime.date.today().year,1,1) + datetime.timedelta(weeks=datetime.date.today().isocalendar()[1]-1), last=False):
    #print(date_start)
    global goals_id_list  #id from fenction to function
    goals_id_list = []
    global week_begin
    week_begin=date_start
    #set primary date
    # a.strftime("%A, %d %B %Y").upper()
    # c = datetime.datetime.strptime(b, "%A, %d %B %Y")
    date_start_block = App.get_running_app().root.ids.application_screen.ids._target_window.ids._goals_plan.ids._start_week_date
    date_today_block = App.get_running_app().root.ids.application_screen.ids._target_window.ids._goals_plan.ids._today_date
    goal_plan = App.get_running_app().root.ids.application_screen.ids._target_window.ids._goals_plan
    goals_plan_place = goal_plan.ids._goals_plan_place
    goals_plan_place.bind(minimum_height=goals_plan_place.setter('height'))
    summary_place = App.get_running_app().root.ids.application_screen.ids._target_window.ids._goals_plan.ids._summary_place



    date_end = date_start + datetime.timedelta(days=6)
    if last == False:
        date_start_block.text = "WEEK {},  {} - {} {}".format(date_start.isocalendar()[1], date_start.strftime("%d"), date_end.strftime("%d"), date_start.strftime("%B %Y").upper())
        date_today_block.text = date_start.strftime("%A, %d %B %Y").upper()
    else:
        next_week = date_start+datetime.timedelta(weeks=1)
        date_start_block.text = "WEEK {},  {} - {} {}".format(next_week.isocalendar()[1], next_week.strftime("%d"),date_end.strftime("%d"),next_week.strftime("%B %Y").upper())
        date_today_block.text = next_week.strftime("%A, %d %B %Y").upper()
   #Top block Days of week MON TUE WED ...
   # blocks = ['_one_day', '_two_day', '_three_day', '_four_day', '_five_day', '_six_day', '_seven_day']
   # for day,block in enumerate(blocks):
   #     day_of_week = date_start + datetime.timedelta(days=day)
   #     goal_plan.ids[block].text = day_of_week.strftime("%a").upper()


    for child in goals_plan_place.children[:]: #remove last widgets
        goals_plan_place.remove_widget(child)

    blocks = ['_one', '_two', '_three', '_four', '_five', '_six', '_seven']
    result = select_from_db("select icon, title, id from goals where user_id = ? order by pos", gl.USER_ID)
    for i, v in enumerate(result):
        gc = GoalPlanContainer(result[i][0], result[i][1])  # icon, title
        goals_id_list.append(result[i][2])
        hour_intervals = select_from_db("select hours_interval from goals_plan where goal_id = ? and date_start=?", result[i][2],date_start)
        gc.ids._hours_week.text = hour_intervals[0][0] if hour_intervals else ''

        for days,block in enumerate(blocks):
            today = date_start + datetime.timedelta(days = days)
            hour_days = select_from_db("select hours from goals_plan_daily where goal_id = ? and day_date=?", result[i][2], today)
            gc.ids[block].text = hour_days[0][0] if hour_days else ''
        goals_plan_place.add_widget(gc)

    goals_id_list = goals_id_list[::-1]

    zero = datetime.timedelta(0)
    summary = {'_sum_hours_week': zero, '_sum_one':zero, '_sum_two': zero, '_sum_three': zero, '_sum_four': zero ,'_sum_five': zero, '_sum_six': zero, '_sum_seven': zero}
    for child in goals_plan_place.children[:]:
        summary['_sum_hours_week'] += text_to_timedelta(child.ids._hours_week.text)
        summary['_sum_one'] += text_to_timedelta(child.ids._one.text)
        summary['_sum_two'] += text_to_timedelta(child.ids._two.text)
        summary['_sum_three'] += text_to_timedelta(child.ids._three.text)
        summary['_sum_four'] += text_to_timedelta(child.ids._four.text)
        summary['_sum_five'] += text_to_timedelta(child.ids._five.text)
        summary['_sum_six'] += text_to_timedelta(child.ids._six.text)
        summary['_sum_seven'] += text_to_timedelta(child.ids._seven.text)
    sleep = select_from_db("select bedtime, wakeup from sleeptime where user_id = ?", gl.USER_ID)

    week_work_time=timedelta_to_text(7*(sleep[0][0]-sleep[0][1]))
    day_work_time=timedelta_to_text(sleep[0][0]-sleep[0][1])
    for key, value in summary.items():
        summary_place.ids[key].text =  timedelta_to_text(value) + '/'
        summary_place.ids[key].text += week_work_time if key == '_sum_hours_week' else day_work_time


def text_to_timedelta(text_hours):
    if text_hours == '':
        return datetime.timedelta(hours = 0, minutes = 0)
    else:
        return datetime.timedelta(hours = int(text_hours[:1]) if len(text_hours) == 4 else int(text_hours[:2]),minutes = int(text_hours[-2:]))

def timedelta_to_text(timedelta_obj):
    hours = int(timedelta_obj.total_seconds()/3600)
    min =  str(int((timedelta_obj.total_seconds()%3600)/60)) if (timedelta_obj.total_seconds()%3600)/60>9 else '0' + str(int((timedelta_obj.total_seconds()%3600)/60))
    return "{}:{}".format(hours, min)

class TimeCounterPlan(TimeCounter):
    pass




class BlockCustomHour(ToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._update_container)

    def _update_container(self, dt):
        self.bind(on_press=self.check_state)


    def check_state(self, *args):
        goal_plan_container = self.parent.parent
        if self.state == 'down' and goal_plan_container.state == 'normal':
            goal_plan_container.state = 'down'
        if self.state == 'normal' and goal_plan_container.state == 'down':
            goal_plan_container.state = 'normal'


        #blocks = ['_hours_week', '_monday', '_tuesday', '_wednesday', '_thursday', '_friday', '_saturday', '_sunday']
        for child in goal_plan_container.parent.children:
            if child.state == 'down' and goal_plan_container.state == 'down':
                child.state = 'normal'
                goal_plan_container.state = 'down'


class GoalPlanContainer(ToggleButton):
    def __init__(self, icon, title, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.title = title
        Clock.schedule_once(self._update_container)

    def _update_container(self, dt):
        self.ids._title.text = self.title
        self.bind(on_press=self.check_state)
        self.parent.bind(minimum_height=self.parent.setter('height'))
        with self.ids._icon.canvas:
            Rectangle(pos=(10,10), size=(40,40), source='Settings/images/goals/' + self.icon)


    def check_state(self, *args):
        #blocks = ['_hours_week', '_monday', '_tuesday', '_wednesday', '_thursday', '_friday', '_saturday', '_sunday']
        blocks=['_hours_week', '_one', '_two', '_three', '_four', '_five', '_six', '_seven']
        for block in blocks:
            if self.ids[block].state == 'down' and self.state == 'normal':
                self.ids[block].state = 'normal'

        for child in self.parent.children:
            for block in blocks:
                if child.ids[block].state == 'down' and self.state == 'down':
                    child.ids[block].state = 'normal'



class GoalsPlan(Screen):
    #def __init__(self, **kwargs):
    #    super().__init__(**kwargs)
    #    Clock.schedule_once(self._update_container)

    #def _update_container(self, dt):
    #    goals_plan_place = self.ids._goals_plan_place
    #    goals_plan_place.bind(minimum_height=goals_plan_place.setter('height'))
    #    for i in range(8):
    #        goals_plan_place.add_widget(GoalPlanContainer())


    def save_goals_plan(self):
        global goals_id_list
        week_begin = datetime.datetime.strptime(self.ids._today_date.text, "%A, %d %B %Y").date()
        print(week_begin)
        blocks = ['_one', '_two', '_three', '_four', '_five', '_six', '_seven']

        for index, child in enumerate(self.ids._goals_plan_place.children):
            if child.ids._hours_week.text == '0:00' or child.ids._hours_week.text == '':
                conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                cursor = conn.cursor()
                cursor.execute("delete from goals_plan where date_start=? and goal_id=?", (week_begin, goals_id_list[index]))
                conn.commit()
                conn.close()
                #child.ids._hours_week.text = ''

            else:
                conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                cursor = conn.cursor()
                cursor.execute("insert or ignore into goals_plan (id, date_start, goal_id) values((select id from goals_plan where date_start=? and goal_id=?),?,?)",(week_begin, goals_id_list[index],week_begin, goals_id_list[index]))
                conn.commit()
                cursor.execute("update goals_plan set hours_interval=? where date_start=? and goal_id=?",(child.ids._hours_week.text, week_begin, goals_id_list[index],))
                conn.commit()
                #result = cursor.fetchall()
                conn.close()

            for days, block in enumerate(blocks):
                today = week_begin + datetime.timedelta(days=days)
                if child.ids[block].text == '0:00' or child.ids[block].text == '':
                    conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                    cursor = conn.cursor()
                    cursor.execute("delete from goals_plan_daily where day_date=? and goal_id=?",(today, goals_id_list[index]))
                    conn.commit()
                    conn.close()
                else:
                    conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                    cursor = conn.cursor()
                    cursor.execute("insert or ignore into goals_plan_daily (id, day_date, goal_id) values((select id from goals_plan_daily where day_date=? and goal_id=?),?,?)",
                        (today, goals_id_list[index], today, goals_id_list[index]))
                    conn.commit()
                    cursor.execute("update goals_plan_daily set hours=? where day_date=? and goal_id=?",
                                   (child.ids[block].text, today, goals_id_list[index],))
                    conn.commit()
                    conn.close()

        chose_date = datetime.datetime.strptime(self.ids._today_date.text, "%A, %d %B %Y")
        display_place_plan_goals(datetime.date(datetime.date.today().year, 1, 1) + datetime.timedelta(weeks=chose_date.isocalendar()[1] - 1))
        print('Complete')

    def cancel_goals_plan(self):
        chose_date = datetime.datetime.strptime(self.ids._today_date.text, "%A, %d %B %Y")
        display_place_plan_goals(datetime.date(datetime.date.today().year, 1, 1) + datetime.timedelta(weeks=chose_date.isocalendar()[1] - 1))

    def clean_all(self):
        blocks = ['_hours_week', '_one', '_two', '_three', '_four', '_five', '_six', '_seven']
        for child in self.ids._goals_plan_place.children:
            for block in blocks:
                child.ids[block].text = ''


    def repeat_last_week(self):
        chose_date = datetime.datetime.strptime(self.ids._today_date.text, "%A, %d %B %Y")
        display_place_plan_goals(datetime.date(datetime.date.today().year, 1, 1) + datetime.timedelta(weeks=chose_date.isocalendar()[1] - 2), True)

class DatePopup(Popup):
    def __init__(self, last_date_block, **kwargs):
        super().__init__(**kwargs)
        self.last_date_block = last_date_block
        Clock.schedule_once(self._update_container)
    def _update_container(self, dt):
        # a.strftime("%A, %d %B %Y").upper()
        # c = datetime.datetime.strptime(b, "%A, %d %B %Y")
        self.ids._date.text = self.last_date_block.text
        self.ids._week.text = "WEEK {}".format(datetime.datetime.strptime(self.last_date_block.text, "%A, %d %B %Y").isocalendar()[1])
        self.ids._left.bind(on_press=self.minus_date)
        self.ids._right.bind(on_press=self.plus_date)
        self.ids._save_btn.bind(on_press=self.save_btn)

    def minus_date(self, *args):
        chose_date = datetime.datetime.strptime(self.ids._date.text, "%A, %d %B %Y") - datetime.timedelta(days=1)
        self.ids._date.text = chose_date.strftime("%A, %d %B %Y").upper()
        self.ids._week.text = "WEEK {}".format(chose_date.isocalendar()[1])
    def plus_date(self, *args):
        chose_date = datetime.datetime.strptime(self.ids._date.text, "%A, %d %B %Y") + datetime.timedelta(days=1)
        self.ids._date.text = chose_date.strftime("%A, %d %B %Y").upper()
        self.ids._week.text = "WEEK {}".format(chose_date.isocalendar()[1])

    def save_btn(self, *args):
        chose_date = datetime.datetime.strptime(self.ids._date.text, "%A, %d %B %Y")
        display_place_plan_goals(datetime.date(datetime.date.today().year,1,1) + datetime.timedelta(weeks=chose_date.isocalendar()[1]-1))



class Timebtnph(Label):
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            time = self.parent.parent
            last = time.text
            time.text = clock_hour(time, time.text , '+')
            time.parent.hours_week.text = clock_week_hour(time.parent.hours_week.text, last, time.text)

            time.state = 'normal'
class Timebtnmh(Label):
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            time = self.parent.parent
            last = time.text
            time.text = clock_hour(time, time.text , '-')
            time.parent.hours_week.text = clock_week_hour(time.parent.hours_week.text, last, time.text)
            time.state = 'normal'

class Timebtnpm(Label):
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            time = self.parent.parent
            last = time.text
            time.text = clock_minutes(time, time.text, '+')
            time.parent.hours_week.text = clock_week_hour(time.parent.hours_week.text, last, time.text)
            time.state = 'normal'
class Timebtnmm(Label):

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            time = self.parent.parent
            last = time.text
            time.text = clock_minutes(time, time.text, '-')
            time.parent.hours_week.text = clock_week_hour(time.parent.hours_week.text, last, time.text)
            time.state = 'normal'

def clock_hour(time_block, last_time, sign):
    if last_time =='':
        return '0:00'
    elif time_block.state =='down':
        hour = int(last_time[:2])  if len(last_time)==5 else int(last_time[:1])# first two or one numbers from 0:00 or 12:00
        if sign == '+':
            hour+=1
        elif sign == '-':
            hour-=1
        if hour>23:
            return '0'+ last_time[-3:] #00 + :00
        if 0<=hour<10:
            return str(hour) + last_time[-3:] #0 + :00
        if hour<0:
            return '23' + last_time[-3:]
        return str(hour) + last_time[-3:]
    return last_time

def clock_minutes(time_block, last_time, sign):
    if last_time =='':
        return '0:00'
    elif time_block.state == 'down':
        minute = int(last_time[-2:])# last two numbers from 00:00
        hour = last_time[:3] if len(last_time) == 5 else last_time[:2]
        if sign == '+':
            minute+=15
        elif sign == '-':
            minute-=15

        if minute>=60:
            hour = clock_hour(time_block, last_time, '+')
            hour = hour[:3] if len(hour) == 5 else hour[:2]
            return  hour + '00'
        if minute==0:
            return hour + '00'
        if minute<0:
            hour = clock_hour(time_block, last_time, '-')
            hour = hour[:3] if len(hour) == 5 else hour[:2]
            return hour + '45'
        return hour + str(minute)
    return last_time

def clock_week_hour(hours_week, last_day_time, new_day_time):
    week = text_to_timedelta(hours_week)
    last = text_to_timedelta(last_day_time)
    new = text_to_timedelta(new_day_time)
    return timedelta_to_text(week-last+new)
