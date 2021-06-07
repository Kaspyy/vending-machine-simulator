import unittest
from AutomatUX import *

"""Klasa zawierająca testy jednostkowe systemu automatu"""
class VendingMachineTest(unittest.TestCase):

    def setUp(self):
        """Metoda inicjująca automat"""
        self.machine = Machine()

    def test_get_product_price(self):
        """Sprawdzenie ceny jednego towaru - oczekiwana informacja o cenie."""
        self.assertEqual(350, self.machine.get_product_price(38))

    def test_no_change(self):
        """Wrzucenie odliczonej kwoty, zakup towaru - oczekiwany brak reszty."""
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)

        result = self.machine.payment(32)
        self.assertEqual('Brak reszty.', result[0])

    def test_get_change(self):
        """Wrzucenie większej kwoty, zakup towaru - oczekiwana reszta."""
        self.machine.coins[10]['owned'] = 1

        self.machine.insert_coin(200)
        self.machine.insert_coin(20)
        self.machine.insert_coin(20)
        self.machine.insert_coin(20)

        result = self.machine.payment(32)
        self.assertEqual({10: 1}, result[0])

    def test_out_of_stock(self):
        """Wykupienie całego asortymentu,
        próba zakupu po wyczerpaniu towaru - oczekiwana informacja o braku."""
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)
        self.machine.payment(32)
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)
        self.machine.payment(32)
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)
        self.machine.payment(32)
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)
        self.machine.payment(32)
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)
        self.machine.payment(32)
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)

        self.assertRaises(ProductUnavailableException, self.machine.payment, 32)

    def test_get_non_existing_product_price(self):
        """Sprawdzenie ceny towaru o nieprawidłowym numerze (<30 lub >50)
        - oczekiwana informacja o błędzie."""
        self.assertRaises(IncorrectProductNumberException, self.machine.get_product_price, 3)

    def test_withdraw_money(self):
        """Wrzucenie kilku monet, przerwanie transakcji - oczekiwany zwrot monet."""
        self.machine.insert_coin(200)
        self.machine.insert_coin(50)
        self.machine.insert_coin(10)
        self.machine.insert_coin(50)
        self.assertEqual({10: 1, 50: 2, 200: 1}, self.machine.withdraw())

    def test_add_more_coins(self):
        """Wrzucenie za małej kwoty, wybranie poprawnego numeru towaru,
        wrzucenie reszty monet do odliczonej kwoty,
        ponowne wybranie poprawnego numeru towaruoczekiwany brak reszty."""
        self.machine.insert_coin(100)
        self.machine.insert_coin(50)
        self.assertRaises(NotEnoughMoneyException, self.machine.payment, 32)

        self.machine.insert_coin(100)
        result = self.machine.payment(32)
        self.assertEqual('Brak reszty.', result[0])

    def test_pay_in_cents(self):
        """Zakup towaru płacąc po 1 gr - suma stu monet ma być równa 1zł."""
        for i in range(250):
            self.machine.insert_coin(1)
        result = self.machine.payment(32)
        self.assertEqual('Brak reszty.', result[0])

if __name__ == '__main__':
    unittest.main()