from kivy.core.window import Window
from kivy.lang import Builder

from kivymd.app import MDApp

from container import Container

Window.size = (320, 550)


class WorkApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"
    title = 'work app'

    def build(self):
        Builder.load_file('dialogcontent.kv')
        Builder.load_file('carditem.kv')
        Builder.load_file('paycarditem.kv')
        return Container()


if __name__ == '__main__':
    WorkApp().run()
