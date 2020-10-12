import smtplib

from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.snackbar import Snackbar
from sqlalchemy.orm import Session

from appdata import engine, Visit, Oil


class DialogContent(BoxLayout):
    def send_email(self):
        if self.email_dialog_input.text:
            oil_list = []
            visit_list = []
            session = Session(bind=engine)
            visit = session.query(Visit).all()
            oil = session.query(Oil).all()
            for i in oil:
                oil_list.append([i.id, i.month, i.date, i.pay, i.comment])
            for i in visit:
                visit_list.append(
                    [i.id, i.month, i.date, i.type, i.name, i.address, i.distance, i.money])

            smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
            smtpObj.starttls()
            smtpObj.login('python.app159@gmail.com', 'Sasha.1794')
            smtpObj.sendmail("python.app159@gmail.com", self.email_dialog_input.text,
                             f'{oil_list}\n{visit_list}'.replace(':', '/..').encode('utf-8'))

            Snackbar(
                text=f'Данные были отправленны на {self.email_dialog_input.text}').show()

            self.email_dialog_input.text = ''

            smtpObj.quit()

        else:
            Snackbar(text='Данные не были отправленны, введите gmail').show()
