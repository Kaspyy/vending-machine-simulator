from tkinter import *

"""Wyjątki"""


class MachineException(Exception):

    def __init__(self, msg):
        self.msg = msg


"""IncorrectProductNumberException - wyjątek podnoszony w momencie podania numeru <30 lub >50"""


class IncorrectProductNumberException(MachineException):
    def __init__(self):
        super().__init__("Niepoprawny numer produktu!")


"""NotEnoughMoneyException - podnoszony w momencie, w którym wrzucona kwota jest mniejsza od ceny produktu"""


class NotEnoughMoneyException(MachineException):
    def __init__(self, price):
        super().__init__("Niewystarczająca ilość pieniędzy!\nCena produktu: " + str(price/100) + " zł.")


"""OnlyExactMoneyException - podnoszony, gdy automat nie posiada monet, aby zwrócić resztę"""


class OnlyExactMoneyException(MachineException):
    def __init__(self):
        super().__init__("Tylko odliczona kwota.")


"""ProductUnavailableException - podnoszony, gdy wyczerpany zostanie zapas produktu w automacie"""


class ProductUnavailableException(MachineException):
    def __init__(self):
        super().__init__('Produkt niedostępny.')


"""WithdrawException - podnoszony, gdy użytkownik przerwie tranakcję, ale nie wrzucił żadnych monet"""


class WithdrawException(MachineException):
    def __init__(self):
        super().__init__('Nie wrzucono żadnych monet.')


"""Klasa przedmiotu"""


class Item:
    def __init__(self, name):
        self.name = name


"""Klasa Product, dziedzicząca po klasie Item, zawierająca pole ceny: price oraz quantity: liczbę sztuk"""


class Product(Item):
    def __init__(self, name, price):
        super(Product, self).__init__(name)
        self.price = price
        self.quanity = 5


"""Klasa Machine"""


class Machine:
    coin_types = [1, 2, 5, 10, 20, 50, 100, 200, 500]
    coins = None

    products = {}
    chosen = None

    def __init__(self):
        """Konstruktor klasy Machine"""
        super().__init__()

        self.init_products()

        self.init_coins_dicts()

        self.get_inserted()

    def init_coins_dicts(self):
        """Metoda inicjująca słownik z monetami"""
        self.coins = {}
        for c in self.coin_types:
            self.coins[c] = {
                'owned': 1,
                'inserted': 0
            }

    def get_inserted(self):
        """Metoda pobierająca wrzucone monety"""
        return {key: self.coins[key]['inserted'] for key, value in self.coins.items() if
                self.coins[key]['inserted'] > 0}

    def get_inserted_value(self):
        """Metoda pobierająca kwotę wrzuconych monet"""
        v = 0
        for key, value in self.coins.items():
            v += key * value['inserted']
        return v

    def get_coin_amount(self, dict):
        """Metoda pobierająca liczbę wrzuconych monet"""
        counter = 0
        for key, value in dict.items():
            counter += value
        return counter

    def connect_coin_dict(self, dict1, dict2):
        """Metoda łącząca słowniki z monetami"""
        result = dict1.copy()
        for key in dict2:
            if key in result:
                result[key] += dict2[key]
            else:
                result[key] = dict2[key]
        return result

    def check_available_coins(self, dict):
        """Metoda sprawdzająca dostępne monety do wydania reszty"""
        for key, value in dict.items():
            available = self.coins[key]['owned'] + self.coins[key]['inserted']
            if value > available:
                return False
        return True

    def payment(self, product_number):
        """Metoda odpowiedzialna za przeprowadzenie płatności,
        w tym wydawanie produktu i ewentualne zwracanie reszty."""
        if product_number not in self.products:
            raise IncorrectProductNumberException

        product = self.products[product_number]
        if product.quanity < 1:
            raise ProductUnavailableException
        price = product.price
        inserted = self.get_inserted_value()
        change = inserted - price
        if change < 0:
            raise NotEnoughMoneyException(self.products[product_number].price)
        elif change == 0:
            product.quanity -= 1
            self.clear_inserted()
            return 'Brak reszty.', product

        temp_dict = {}
        for key, value in self.coins.items():
            temp_dict[key] = value['owned']
            temp_dict[key] += value['inserted']

        past_dict = {0: {}}
        for i in range(1, change + 1):
            for coin in self.coin_types:
                rest = i - coin
                if rest < 0:
                    continue

                if rest not in past_dict:
                    continue

                dict = {coin: 1}
                new_dict = self.connect_coin_dict(
                    past_dict[rest],
                    dict
                )

                if not self.check_available_coins(new_dict):
                    continue
                if i not in past_dict:
                    past_dict[i] = new_dict
                else:
                    if self.get_coin_amount(past_dict[i]) > self.get_coin_amount(new_dict):
                        past_dict[i] = new_dict

        if change not in past_dict:
            raise OnlyExactMoneyException

        for key in self.coins:
            self.coins[key]['owned'] += self.coins[key]['inserted']
        for key in past_dict[change]:
            self.coins[key]['owned'] -= past_dict[change][key]

        self.clear_inserted()

        product.quanity -= 1

        return past_dict[change], product

    def get_product_price(self, product_number):
        """Metoda zwracająca cenę danego produktu"""
        if product_number not in self.products:
            raise IncorrectProductNumberException
        return self.products[product_number].price

    def withdraw(self):
        """Metoda odpowiedzialna za procedurę przerwania płatności, zwraca wrzucone monety"""
        if self.get_inserted_value() == 0:
            raise WithdrawException
        result = self.get_inserted().copy()
        self.clear_inserted()
        return result

    def clear_inserted(self):
        """Metoda odpowiedzialna za usunięcie wrzuconych monet"""
        for key in self.coins:
            self.coins[key]['inserted'] = 0

    def insert_coin(self, v):
        """Metoda odpowiedzialna za wrzucanie monet, zwiększa wartość pola inserted o 1"""
        self.coins[v]['inserted'] += 1

    def init_products(self):
        """Metoda inicjująca dostępne produkty"""
        self.products[30] = Product("Cisowianka 0.3l", 150)
        self.products[31] = Product("Cisowianka 0.5l", 200)
        self.products[32] = Product("Coca-Cola 0.33l", 250)
        self.products[33] = Product("Coca-Cola 0.5l", 500)
        self.products[34] = Product("Sprite 0.33l", 250)
        self.products[35] = Product("Sprite 0.5l", 500)
        self.products[36] = Product("Fanta 0.33l", 250)
        self.products[37] = Product("Fanta 0.5l", 500)
        self.products[38] = Product("Lipton 0.33l", 350)
        self.products[39] = Product("Lipton 0.5l", 450)
        self.products[40] = Product("Tiger 0.20l", 350)
        self.products[41] = Product("RedBull 0.20l", 890)
        self.products[42] = Product("Mirinda 0,33l", 150)
        self.products[43] = Product("Mirinda 0,5l", 400)
        self.products[44] = Product("Tonic 0.33l", 320)
        self.products[45] = Product("Tonic 0.5l", 470)
        self.products[46] = Product("Monster 0,5l", 500)
        self.products[47] = Product("Muszyna gaz 0,2l", 130)
        self.products[48] = Product("Muszyna gaz 0,33l", 200)
        self.products[49] = Product("Muszyna gaz 0,5l", 260)
        self.products[50] = Product("Pepsi 0.33l", 250)
