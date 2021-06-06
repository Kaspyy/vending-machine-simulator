from tkinter import messagebox
from functools import partial
from tkinter.constants import BOTTOM, LEFT, RIGHT, TOP
from AutomatUX import *

"""Klasa ramki okna"""
class BorderFrame(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.configure(borderwidth=2, relief="ridge")

"""Klasa interfejsu z monetami"""
class CoinUI(BorderFrame):
    def __init__(self, machine):
        super().__init__()

        self.machine = machine
        self.chosen_product = None
        self.coins_value = StringVar()
        self.coins_value.set("0.0")
        self.product_number = StringVar()
        self.product_number.set("")
        self.initUI()

    def add(self, v):
        """Metoda dodająca monetę"""
        self.machine.insert_coin(v)
        self.update_entries()

    def update_entries(self):
        """Metoda akutalizająca wyświetlacz"""
        print(self.machine.get_inserted_value())
        coin_value = self.machine.get_inserted_value()
        self.coins_value.set(float("{0:.2f}".format(coin_value / 100)))

    def initUI(self):
        """Metoda inicjująca interfejs z monetami i numpadem"""
        self.master.title("Review")
        self.pack(fill=BOTH, expand=True, pady = 50)

        counter = 0
        frame = BorderFrame(self)
        frame.pack(side = TOP, pady = 20)
        for key, value in self.machine.coins.items():
            if counter % 3 == 0:
                f = Frame(frame)
                f.pack()
            part = partial(self.add, key)
            if float(key) < 100:
                text = str(int(key)) + " gr"
            else:
                text = str(int(key / 100)) + " zł"

            button = Button(f, command=part, text=text, width=6)
            button.pack(side=LEFT, padx=5, pady=5)
            counter += 1

        f = BorderFrame(self)
        f.pack()
        frame = Frame(f)
        frame.pack()
        label = Label(frame, text="Kwota")
        label.pack(side=LEFT, padx=5, pady=5)
        entry = Entry(frame, textvariable=self.coins_value, state='readonly', justify='right', width=12)
        entry.pack(padx=5, pady=5)

        frame = Frame(f)
        frame.pack()
        label = Label(frame, text="Numer")
        label.pack(side=LEFT, padx=5, pady=5)
        entry = Entry(frame, textvariable=self.product_number, state='readonly', justify='right', width=12)
        entry.pack(padx=5, pady=5)

        frame = BorderFrame(self)
        frame.pack(pady = (20, 10))
        for i in range(1, 11):
            if i % 3 == 1:
                f = Frame(frame)
                f.pack()
            if i == 10:
                button = Button(f, command=lambda:self.numpad_click(-2), text='Clear', width=6)
                button.pack(side=LEFT, padx=5, pady=5)
            part = partial(self.numpad_click, i % 10)
            button = Button(f, command=part, text=i % 10, width=6)
            button.pack(side=LEFT, padx=5, pady=5)
            if i == 10:
                button = Button(f, command=lambda:self.numpad_click(-1), text='<', width=6)
                button.pack(side=LEFT, padx=5, pady=5)

        f = BorderFrame(self)
        f.pack()
        frame = Frame(f)
        frame.pack()
        button = Button(frame, command=lambda:self.withdraw(), text="Przerwij", width=6)
        button.pack(side=LEFT, padx=5, pady=5)
        button = Button(frame, command=lambda:self.pay(), text="Zapłać", width=6)
        button.pack(side=LEFT, padx=5, pady=5)

    def numpad_click(self, v):
        """Metoda odpowiedzialna za działanie okienka z numpadem"""
        if v == -1:
            number = self.product_number.get()
            if len(number) > 1:
                number = int(number)
                number /= 10
                self.product_number.set(int(number))
            else:
                self.product_number.set('')
        elif v == -2:
            self.product_number.set("")
        elif v == -9:
            print(self.machine.coins)
        else:
            number = self.product_number.get()
            if len(number) > 0:
                number = int(number)
                number *= 10
                v += number
            self.product_number.set(v)

    def pay(self):
        """Metoda odpowiedzialna za przeprowadzenie transakcji: wydanie produktu oraz reszty"""
        if self.product_number.get() == '':
            return
        else:
            try:
                value, product = self.machine.payment(int(self.product_number.get()))
                info_1 = "Zakupiony produkt:\n\n" + product.name + '\n\n'
                if type(value) is str:
                    messagebox.showinfo('OK', info_1 + value)
                else:
                    info_2 = "Reszta:\n"
                    for k, v in value.items():
                        if k < 100:
                            t = str(int(k)) + ' gr'
                        else:
                            t = str(int(k / 100)) + ' zł'
                        info_2 += "\n" + str(int(v)) + ' x ' + t
                    messagebox.showinfo('OK', info_1 + info_2)

                self.product_number.set('')
                self.update_entries()
            except MachineException as e:
                messagebox.showinfo('Error', e.msg)

    def withdraw(self):
        """Metoda odpowiedzialna za przerwanie transakcji, zwracająca wrzucone pieniądze"""
        try:
            value = self.machine.withdraw()
            info_1 = "Wypłacono:"
            for k in value:
                if k < 100:
                    t = str(int(k)) + ' gr'
                else:
                    t = str(int(k / 100)) + ' zł'
                info_1 += "\n" + str(int(value[k])) + ' x ' + t
            messagebox.showinfo('OK', info_1)
            self.product_number.set('')
            self.update_entries()
        except MachineException as e:
            messagebox.showinfo('Warning', e.msg)

    def set_chosen(self, product):
        """Metoda pobierająca wybrany produkt"""
        if product is not None:
            self.chosen_product = product
        else:
            self.chosen_product = None

        self.update_entries()

"""Klasa reprezantująca okno z produktami,
dziedzicząca po klasie BorderFrame"""
class ProductsUI(BorderFrame):
    def __init__(self, machine, coin_ui):
        super().__init__()

        self.machine = machine
        self.coin_ui = coin_ui
        self.coins_value = StringVar()
        self.coins_value.set("0.0")

        self.chosen = None

        self.initUI()

    def choose(self, product, button):
        """Metoda odpowiedzialna za efekt wizualny wciskania przycisków oraz wybór produktu"""
        if self.chosen is not None:
            self.chosen.configure(relief=RAISED)
            if self.chosen is button:
                self.chosen = None
                self.coin_ui.set_chosen(None)
                return

        self.chosen = button
        button.configure(relief=SUNKEN)

        self.coin_ui.set_chosen(product)

    def initUI(self):
        """Metoda inicjująca interfejs okna produktów"""
        self.master.title("Automat sprzedający napoje")
        self.pack(fill=BOTH, expand=True)

        counter = 0
        f = None
        for id, product in self.machine.products.items():
            if counter % 4 == 0:
                f = Frame(self)
                f.pack()

            product_frame = Frame(f, borderwidth=2, relief="ridge")
            Label(product_frame, text=str(id), width=11).pack(padx=5, pady=2)
            Label(product_frame, text=str(product.name)).pack(padx=5, pady=2)
            Label(product_frame, text="Cena: " + str("{0:.2f}".format(product.price / 100))).pack(padx=5, pady=2)

            product_frame.pack(side=LEFT, padx=5, pady=5)
            counter += 1

"""Klasa Program odpowiedzialna za ustawienie intefejsu"""
class Program(Frame):

    def __init__(self):
        super().__init__()

        self.machine = Machine()
        self.initUI()

    def initUI(self):
        self.master.title("Coin machine")

        coin_ui = CoinUI(self.machine)
        product_ui = ProductsUI(self.machine, coin_ui)

        product_ui.pack(side=LEFT)
        coin_ui.pack(side=RIGHT)


def main():
    root = Tk()
    Program()
    root.geometry("700x550+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
