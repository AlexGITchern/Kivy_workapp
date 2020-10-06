import smtplib
from datetime import datetime

from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.card import MDCardSwipe, MDSeparator
from kivymd.uix.snackbar import Snackbar
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Window.size = (320, 550)
engine = create_engine('sqlite:///appdata.db', echo=False)
base = declarative_base()


class Visit(base):
    __tablename__ = 'visit'
    id = Column(Integer, primary_key=True)
    month = Column(String)
    date = Column(String)
    type = Column(String)
    name = Column(String)
    address = Column(String)
    distance = Column(Integer)
    money = Column(Integer)


class Oil(base):
    __tablename__ = 'oil'
    id = Column(Integer, primary_key=True)
    month = Column(String)
    date = Column(String)
    pay = Column(Integer)
    comment = Column(String)


base.metadata.create_all(engine)


class Container(ScreenManager):
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    DAYS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

    MONTH = int(datetime.now().strftime("%m")) - 1
    YEAR = int(datetime.now().strftime('%Y'))

    COUNT_STR = 0
    COUNT_MONEY = 0
    COUNT_DISTANCE = 0
    COUNT_PAY = 0

    def set_visit(self):
        visit_type = self.visit_type.text
        name = self.name.text
        address = self.address.text
        distance = self.distance.text
        session = Session(bind=engine)
        if visit_type and name and address and distance:
            visit = Visit(month=Container.MONTHS[Container.MONTH],
                          date=str(datetime.now())[:16] + '-' + str(datetime.now().weekday()), type=visit_type,
                          name=name, address=address, distance=distance, money=0)
            session.add(visit)
            session.commit()
            self.visit_type.text = ''
            self.name.text = ''
            self.address.text = ''
            self.distance.text = ''
            Snackbar(text='Добавлено').show()

        session.close()

    def set_margin(self):
        money = self.money.text
        comment = self.money_comment.text
        session = Session(bind=engine)
        money = Visit(month=datetime.now().strftime("%B"),
                      date=str(datetime.now())[:16] + '-' + str(datetime.now().weekday()), distance=0, money=money,
                      name=comment)
        session.add(money)
        session.commit()
        self.money.text = ''
        self.money_comment.text = ''
        Snackbar(text='Добавлено').show()
        session.close()

    def set_oil(self):
        pay = self.pay.text
        comment = self.pay_comment.text
        session = Session(bind=engine)
        if pay:
            oil = Oil(month=datetime.now().strftime("%B"),
                      date=str(datetime.now())[:16] + '-' + str(datetime.now().weekday()), pay=pay, comment=comment)
            session.add(oil)
            session.commit()
            self.pay.text = ''
            self.pay_comment.text = ''
            Snackbar(text='Добавлено').show()
        session.close()

    def update(self):
        self.main_lbl1.text, self.oil_lbl.text = '', ''
        self.card_list.children = []
        session = Session(bind=engine)
        q = session.query(Visit).all()
        pay = session.query(Oil).all()

        for i in q:
            if i.month == Container.MONTHS[Container.MONTH] and int(i.date[:4]) == Container.YEAR:
                if i.money == 0:
                    self.card_list.add_widget(
                        CardItem(text=f'{i.date[8:10]}-{Container.DAYS[int(i.date[17:18])]}: {i.type.upper()}',
                                 secondary_text=f'{i.address.title()}',
                                 tertiary_text=f'{i.name.title()}; {i.distance}км'))
                    Container.COUNT_STR += 1
                    Container.COUNT_DISTANCE += i.distance

                if i.money != 0:
                    Container.COUNT_MONEY += i.money
                    self.card_list.add_widget(
                        PayCardItem(
                            text=f'{i.date[8:10]}-{Container.DAYS[int(i.date[17:18])]}: Оплата {i.money} ',
                            secondary_text=f'# {i.name.lower()}'))
                    for a in range(3):
                        self.card_list.add_widget(MDSeparator())

        for w in pay:
            if w.month == Container.MONTHS[Container.MONTH]:
                Container.COUNT_PAY += w.pay
        self.main_lbl1.text = f'Выездов: {Container.COUNT_STR}\nДорога: {Container.COUNT_DISTANCE * 2}км;' \
                              f' {Container.COUNT_PAY}₽\nЗП: {Container.COUNT_MONEY - Container.COUNT_PAY}'
        Container.COUNT_MONEY = 0
        Container.COUNT_STR = 0
        Container.COUNT_DISTANCE = 0
        Container.COUNT_PAY = 0
        self.main_toolbar.title = Container.MONTHS[Container.MONTH]

        # update oil
        for i in pay:
            if i.comment:
                self.oil_lbl.text = f'{i.id})  {i.date[8:10]}-{Container.DAYS[int(i.date[17:18])]}  ' \
                                    f'{i.pay}  ({i.comment})\n\n' + self.oil_lbl.text
            else:
                self.oil_lbl.text = f'{i.id})  {i.date[8:10]}-{Container.DAYS[int(i.date[17:18])]}  {i.pay}\n\n' + \
                                    self.oil_lbl.text
        self.oil_toolbar.text = Container.MONTHS[Container.MONTH]
        session.close()

    def buttl1(self):
        if Container.MONTH == 0:
            Container.MONTH += 12
        Container.MONTH = Container.MONTH - 1
        self.update()

    def buttr1(self):
        if Container.MONTH == 11:
            Container.MONTH -= 12
        Container.MONTH = Container.MONTH + 1
        self.update()

    def send_email(self):
        if self.email_dialog_input.text:
            # self.email_spinner.active = True
            oil_list = []
            visit_list = []
            session = Session(bind=engine)
            visit = session.query(Visit).all()
            oil = session.query(Oil).all()
            for i in oil:
                oil_list.append([i.id, i.month, i.date, i.pay, i.comment])
            for i in visit:
                visit_list.append([i.id, i.month, i.date, i.type, i.name, i.address, i.distance, i.money])

            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.starttls()
            smtpObj.login('python.app159@gmail.com', 'Sasha.1794')
            smtpObj.sendmail("python.app159@gmail.com", self.email_dialog_input.text,
                             f'{oil_list}\n{visit_list}'.replace(':', '/..').encode('utf-8'))
            Snackbar(text=f'Данные были отправленны на {self.email_dialog_input.text}').show()

            smtpObj.quit()

        else:
            Snackbar(text='Данные не были отправленны, введите gmail', button_text='Ввести',
                     button_callback=self.email_dialog.open).show()

    def back_to_home_screen(self):
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = 'main'

    def test_func(self):
        self.card_list.remove_widget(self)


class CardItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()
    tertiary_text = StringProperty()


class PayCardItem(MDCardSwipe):
    text = StringProperty()
    secondary_text = StringProperty()


class WorkApp(MDApp):
    theme_clc = ThemeManager()
    title = 'work app'

    def build(self):
        self.theme_clc.theme_style = 'Dark'
        return Container()


if __name__ == '__main__':
    WorkApp().run()
