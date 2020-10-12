from kivy.properties import StringProperty
from kivymd.uix.card import MDCardSwipe


class CardItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()


class PayCardItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
