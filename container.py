from datetime import datetime

from kivy.uix.screenmanager import ScreenManager

from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDSeparator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar

from sqlalchemy.orm import Session

from appdata import engine, Visit, Oil
from dialog_content import DialogContent
from card_items import PayCardItem, CardItem


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
            if w.month == Container.MONTHS[Container.MONTH] and int(w.date[:4]) == Container.YEAR:
                Container.COUNT_PAY += w.pay
        self.main_lbl1.text = f'Выездов: {Container.COUNT_STR}\nДорога: {Container.COUNT_DISTANCE * 2}км;' \
                              f' {Container.COUNT_PAY}₽\nЗП: {Container.COUNT_MONEY - Container.COUNT_PAY}'
        Container.COUNT_MONEY = 0
        Container.COUNT_STR = 0
        Container.COUNT_DISTANCE = 0
        Container.COUNT_PAY = 0
        self.main_toolbar.title = f'{Container.MONTHS[Container.MONTH]} {Container.YEAR}'

        # update oil
        for i in pay:
            if i.comment:
                self.oil_lbl.text = f'{i.id})  {i.date[8:10]}-{Container.DAYS[int(i.date[17:18])]}  ' \
                                    f'{i.pay}  ({i.comment})\n\n' + \
                    self.oil_lbl.text
            else:
                self.oil_lbl.text = f'{i.id})  {i.date[8:10]}-{Container.DAYS[int(i.date[17:18])]}  {i.pay}\n\n' + \
                                    self.oil_lbl.text
        self.oil_toolbar.text = Container.MONTHS[Container.MONTH]
        session.close()

    def buttl1(self):
        if Container.MONTH == 0:
            Container.MONTH += 12
            Container.YEAR -= 1
        Container.MONTH = Container.MONTH - 1
        self.update()

    def buttr1(self):
        if Container.MONTH == 11:
            Container.MONTH -= 12
            Container.YEAR += 1
        Container.MONTH = Container.MONTH + 1
        self.update()

    def back_to_home_screen(self):
        self.screen_manager.transition.direction = 'right'
        self.screen_manager.current = 'main'

    def open_email_dialog(self):
        self.dialog = MDDialog(title="Введите gmail:", type="custom", size_hint=(0.9, 0.9),
                               content_cls=DialogContent(), buttons=[MDFlatButton(text="CANCEL")])
        self.dialog.buttons[0].on_release = self.dialog.dismiss
        self.dialog.open()
