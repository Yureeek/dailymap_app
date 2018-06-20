from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
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
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout

def select_from_db(query, *args, db='dailymap.db'):
    conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute(query, (*args,))
    result = cursor.fetchall()
    conn.close()
    return result


def display_schedule():
    schedule = App.get_running_app().root.ids.application_screen.ids._schedule_window
    result_place = schedule.ids._result_place
    result_place.bind(minimum_height=result_place.setter('height'))

    for child in result_place.children[:]: #remove last widgets
        result_place.remove_widget(child)
    #for i in range(10):
    #    rb=ResultBlock()
    #    result_place.add_widget(rb)
    result_place.parent.scroll_y = 0

def display_categories():
    schedule = App.get_running_app().root.ids.application_screen.ids._schedule_window
    schedule_manager= schedule.ids._blocks_manager
    home_screen = schedule_manager.get_screen('home_screen')
    categories_place = home_screen.ids._categories_place
    cat_blocks = select_from_db("select id, title, icon, pos from Categories where user_id = ? order by pos", gl.USER_ID)
    #print(schedule_manager.ids)
    #rm = RedScreen(name='red_screen')
    #schedule_manager.add_widget(rm)
    for child in categories_place.children[:]: #remove last widgets
        categories_place.remove_widget(child)

    for i in range(len(cat_blocks)):
        cb=Category(cat_blocks[i][1], cat_blocks[i][2])
        categories_place.add_widget(cb)

        #add subcategories
        sub_blocks = select_from_db("select id, title, icon, influence, pos from Subsections where category_id = ? order by pos", cat_blocks[i][0])
        screen = HomeScreen(name=cat_blocks[i][1])
        for i,v in enumerate(sub_blocks):

            ss = Subsection(sub_blocks[i][1], sub_blocks[i][2])
            screen.ids._categories_place.add_widget(ss)

        schedule_manager.add_widget(screen)


class ResultBlock(ToggleButton):
    def __init__(self, title, time_result = '0:00', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.time_result = time_result
        Clock.schedule_once(self._update)

    def _update(self, dt):
        self.bind(on_press=self.set_info)
        self.ids._title_result.text = self.title
        self.ids._time_result.text = self.time_result
    def set_info(self, *args):
        if self.state=='down':
            self.parent.wid.width=300
            self.parent.center_part.width = 450
        else:
            self.parent.wid.width = 0
            self.parent.center_part.width = 750

class Category(RelativeLayout):
    def __init__(self, title, icon, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.title = title
        Clock.schedule_once(self._update_container)

    def _update_container(self, dt):
        self.ids._title.text = self.title
        #self.bind(on_press=self.set_info)
        with self.ids._icon.canvas:
            Rectangle(pos=(0, 0), size=(60,60), source='Settings/images/goals/' + self.icon)

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos):
            self.parent.parent.manager.current=self.title
            self.parent.parent.manager.title_category.text += " \\ "+self.title
    def set_info(self, *args):
        pass


class Subsection(ToggleButton):
    def __init__(self, title, icon, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.title = title
        Clock.schedule_once(self._update_container)

    def _update_container(self, dt):
        self.ids._subsection_title.text = self.title
        #self.bind(on_press=self.set_info)
        with self.ids._icon.canvas:
            Rectangle(pos=(0, 0), size=(60,60), source='Settings/images/goals/' + self.icon)

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        result_place = self.parent.parent.manager.result_place

        #time_result = result_place.ids._time_result
        if self.collide_point(*touch.pos):
            if self.state == 'down':
                time = ''
                if not result_place.children:
                    # if it's first block
                    #get wake up time (start time)
                    time = self.get_start_time()
                else:
                    # get time from last block
                    time = result_place.children[0].ids._time_result.text[-4:]
                    time = '0h 0min '  + time + ' - ' + time

                self.add_result_block(self.title, time)

                    #result_place.children[0]



    def get_start_time(self):
        start_day = self.parent.parent.manager.start_day.text
        return '0h 0min ' + start_day + ' - '+ start_day
    #def change_time(self):
    #    result_place = self.parent.parent.manager.result_place
    #    time = result_place.ids._time_result


    def add_result_block(self, title, time):
        result_place = self.parent.parent.manager.result_place
        rb = ResultBlock(title, time)
        result_place.add_widget(rb)
        result_place.parent.scroll_y = 0
        result_place.bind(minimum_height=result_place.setter('height'))

class HomeScreen(Screen):
#    def __init__(self, **kwargs):
#        super(HomeScreen, self).__init__(**kwargs)
    pass




class SubScreen(Screen):
    pass
class BlockManager(ScreenManager):
    def __init__(self,**kwargs):
        super(BlockManager,self).__init__(**kwargs)
        Clock.schedule_once(self.setup)

    def home_screen(self, *args):
        if self.current != 'home_screen':
            self.transition.direction = 'right'
        self.current = 'home_screen'
        self.transition.bind(on_complete=self.restart)

    def restart(self, *args):
        self.transition.direction = 'left'
        self.transition.unbind(on_complete=self.restart)




    def setup(self,*args):
        if True:    #under some condition, I want to add ScreenTwo
            #print(self.children, self.current)

            self.add_widget(HomeScreen(name = 'home_screen'))
            #self.add_widget(HomeScreen(name = 'aaa'))
            #self.add_widget(HomeScreen(name='red_screen'))

            self.current = 'home_screen'
            #for i,v in enumerate(self.children):
            #    print(v)
            #print(self.current)
            #print(self.ids)
