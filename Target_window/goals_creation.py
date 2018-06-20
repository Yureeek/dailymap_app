from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from Settings import settings as gl
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Ellipse
import sqlite3
from kivy.graphics import Ellipse
from kivy.graphics import Rectangle
from kivy.app import App
from kivy.clock import Clock
from Target_window.goals_plan import display_place_plan_goals


goal_id = None

def display_place_goals():
    goals_place = App.get_running_app().root.ids.application_screen.ids._target_window.ids._goals_creation.ids._goals_place
    conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.execute("select icon, title, comments, pos, id from goals where user_id = ? order by pos", (gl.USER_ID,))
    result = cursor.fetchall()
    conn.close()
    goals_place.bind(minimum_height=goals_place.setter('height'))
    if goals_place.children:
        for child in goals_place.children[:]:
            goals_place.remove_widget(child)


    for i, v in enumerate(result):
        gc = GoalContainer(result[i][0], result[i][1], result[i][2])  # icon, title, comments
        goals_place.add_widget(gc)



class GoalContainer(ToggleButton):
    def __init__(self, icon, title, comments, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.title = title
        self.comments = comments
        Clock.schedule_once(self._update_container)

    def _update_container(self, dt):
        self.ids._title.text = self.title
        self.ids._comments.text = self.comments
        self.parent.bind(minimum_height=self.parent.setter('height'))
        self.bind(on_press=self.set_info)
        with self.ids._icon.canvas:
            Rectangle(pos=(5, 0), size=(45,45), source='Settings/images/goals/' + self.icon)


    def set_info(self, *args):
        ti = self.parent.title_info
        ci = self.parent.comments_info
        ii = self.parent.image_info
        pi = self.parent.pos_info
        global goal_id
        if self.state != 'down':
            ti.text = ''
            ci.text = ''
            pi.text = ''
            goal_id = None
            with ii.canvas:
                Rectangle(pos=(0, 5), size=(70, 70), source='Settings/images/goals/white.png')
                Rectangle(pos=(0, 5), size=(70, 70), source='Settings/images/navigation/goals_creation_black.png')
            return 0

        ti.text = self.ids._title.text
        ci.text = self.ids._comments.text
        #connect to database and get position and image
        conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("select icon, pos, id from goals where title = ? and user_id = ?", (self.title, gl.USER_ID,))
        result = cursor.fetchall()
        conn.close()
        with ii.canvas:
            Rectangle(pos=(0, 5), size=(70, 70), source='Settings/images/goals/white.png')
            Rectangle(pos=(0, 5), size=(70,70), source='Settings/images/goals/' + result[0][0])
        pi.text = str(result[0][1])  # position
        goal_id = result[0][2] #id


class GoalsCreation(Screen):
    goals_place= ObjectProperty(None)

    def clear_info(self):
        self.ids._title_info.text = ''
        self.ids._comments_info.text = ''
        self.ids._pos_info.text = ''
        with self.ids._image_info.canvas:
            Rectangle(pos=(0, 5), size=(70, 70), source='Settings/images/goals/white.png')
            Rectangle(pos=(0, 5), size=(70, 70), source='Settings/images/navigation/goals_creation_black.png')

    def change_goal(self):
        title = self.ids._title_info.text
        comments = self.ids._comments_info.text
        conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("select count(*) from goals where user_id=?", (gl.USER_ID,))
        amount_of_goals = cursor.fetchall()
        conn.close()
        new_pos=None
        if self.ids._pos_info.text:
            new_pos = int(self.ids._pos_info.text) if 1 <= int(self.ids._pos_info.text) <= amount_of_goals[0][0] else None

        global goal_id
        if title and comments and new_pos and goal_id:
            conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            cursor.execute("select pos from goals where id=?", (goal_id,))
            last_pos = cursor.fetchall()
            last_pos = last_pos[0][0]
            if last_pos > new_pos:
                cursor.execute("select id from goals where pos>=? and pos<? and user_id=?", (new_pos, last_pos, gl.USER_ID,))
                result = cursor.fetchall()
                for value in result:
                    cursor.execute("update goals set pos = pos + 1 where id=? and user_id = ?", (value[0], gl.USER_ID,))
                    conn.commit()
                #cursor.execute("update goals set pos = pos + 1 where id=(select id from goals where ? >= pos < ? and user_id = ?)",(new_pos, last_pos, gl.USER_ID,))
            elif last_pos < new_pos:
                cursor.execute("select id from goals where pos > ? and pos<=? and user_id=?", (last_pos, new_pos, gl.USER_ID,))
                result = cursor.fetchall()
                for value in result:
                    cursor.execute("update goals set pos = pos - 1 where id=? and user_id = ?", (value[0], gl.USER_ID,))
                    conn.commit()
            cursor.execute("update goals set title=?, comments=?, pos=? where id = ?", (title, comments, new_pos, goal_id))
            conn.commit()
            conn.close()
            display_place_goals()
            display_place_plan_goals()
            self.clear_info()
    def add_goal(self):
        conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()
        cursor.execute("select count(*) from goals where user_id =?",(gl.USER_ID,))
        pos = cursor.fetchall()
        pos = str(pos[0][0]+1)
        title = 'New goal {}'.format(pos)
        cursor.execute("insert into goals (user_id, title, icon, comments, pos) values(?,?,?,?,?)", (gl.USER_ID, title, 'book.png', 'Comments', pos))
        conn.commit()
        conn.close()
        display_place_goals()
        display_place_plan_goals()

    def delete_goal(self):
        global goal_id
        if goal_id:
            conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            cursor.execute("select * from goals where id =? and user_id = ?", (goal_id, gl.USER_ID,))
            result = cursor.fetchall()
            conn.close()
            if result:
                conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                cursor = conn.cursor()
                cursor.execute("select * from goals_plan_daily where goal_id =?", (goal_id,))
                in_goals_plan = cursor.fetchall()

                if in_goals_plan:
                    conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                    cursor = conn.cursor()
                    cursor.execute("insert into goals_archive (goal_id, user_id, title, icon, comments) values (?,?,?,?,?)", (goal_id, gl.USER_ID, result[0][2], result[0][3], result[0][4]))
                    conn.commit()
                    conn.close()


                conn = sqlite3.connect('dailymap.db', detect_types=sqlite3.PARSE_DECLTYPES)
                cursor = conn.cursor()
                cursor.execute("delete from goals where id =? and user_id = ?",(goal_id, gl.USER_ID,))
                conn.commit()
                conn.close()
            display_place_goals()
            display_place_plan_goals()
            self.clear_info()
