from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.config import Config
from kivy.properties import ObjectProperty

from Registration_window import registration_main
from NavigationBar import navigationbar_main
from Settings_window import settings_main
from Schedule_window import schedule_main
from Target_window import target_main
Builder.load_file('Settings/settings.kv')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '750')


class Application(BoxLayout):
    pass


class main(App):
    root_registration_manager = ObjectProperty(None)
    root_application_manager = ObjectProperty(None)

    def build(self):
        start_application = Application()
        self.root_registration_manager = start_application.registration_manager  # root screenmanager
        # to create new screen, make "win_screen: app.root_screen_manager' and change its current value
        self.root_application_manager = start_application.application_manager

        return start_application


if __name__ == '__main__':
    main().run()
