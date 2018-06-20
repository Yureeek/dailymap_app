from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.clock import Clock
class TimeCounter(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._update_time)

    def _update_time(self, dt):
        self.ids._up_hour.bind(on_press=self.hour_plus)
        self.ids._up_minute.bind(on_press=self.minute_plus)
        self.ids._down_hour.bind(on_press=self.hour_minus)
        self.ids._down_minute.bind(on_press=self.minute_minus)

    def hour_plus(self, *args):
        self.ids._hour.text = self.clock_hour(self.ids._hour.text, '+')
    def minute_plus(self,*args):
        self.ids._minute.text, self.ids._hour.text = self.clock_minutes(self.ids._minute.text, self.ids._hour.text , '+')
    def hour_minus(self, *args):
        self.ids._hour.text = self.clock_hour(self.ids._hour.text, '-')
    def minute_minus(self,*args):
        self.ids._minute.text, self.ids._hour.text = self.clock_minutes(self.ids._minute.text, self.ids._hour.text , '-')


    def clock_hour(self, last, sign):
        time = int(last)
        if sign == '+':
            time+=1
        elif sign == '-':
            time-=1

        if time>23:
            return '00'
        if 0<=time<10:
            return '0'+ str(time)
        if time<0:
            return '23'
        return str(time)


    def clock_minutes(self, last_minute, last_hour, sign):
        minute = int(last_minute)

        if sign == '+':
            minute+=15
        elif sign == '-':
            minute-=15

        if minute>=60:
            return '00', self.clock_hour(last_hour, '+')
        if minute==0:
            return '00', last_hour
        if minute<0:
            return '45', self.clock_hour(last_hour, '-')
        return str(minute), last_hour

