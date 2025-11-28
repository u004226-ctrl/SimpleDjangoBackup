from django.db import models
from datetime import datetime, timezone
from .recousers import POSITIONS, cashier


# ПРОСТЫЕ ТАБЛИЦЫ БЕЗ ССЫЛОК НА ДРУГИЕ
class Staff(models.Model): # ПРОСТЕЁШАЯ ТАБЛИЦА || СОТРУДНИКИ
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=2, choices=POSITIONS, default=cashier)
    labor_contract = models.IntegerField()


    def get_last_name(self):
        last_name = self.full_name.split()[0]
        return last_name


class Product(models.Model): # ПРОСТЕЙШАЯ ТАБЛИЦА || ПРОДУКТЫ
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0.0)
    composition = models.TextField(default="Состав не указан")


# ТАБЛИЦЫ СВЯЗКИ

class Order(models.Model): # ТАБЛИЦА С ССЫЛКОЙ НА СОТРУДНИКОВ || ЗАКАЗ
    time_in = models.DateTimeField(auto_now_add=True)
    time_out = models.DateTimeField(null=True)
    cost = models.FloatField(default=0.0)
    pickup = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)



    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='ProductOrder') # ССЫЛКА НА ПРОДУКТЫ

    def get_duration(self): # я сделал все правильно без условия :(
        if self.complete:
            seconds = (self.time_in - self.time_out).total_seconds()
            minutes = seconds // 60
            return minutes

        else:  # если ещё нет, то сколько длится выполнение
            return (datetime.now(timezone.utc) - self.time_in).total_seconds() // 60

    def finish_order(self):
        self.time_out = datetime.now()
        self.complete = True
        self.save()


# ТАБЛИЦА КОТОРАЯ ОБЬЕДИНЯЕТ ПРОДУКТЫ И ЗАКАЗ || ВЕРШИНА
class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    _amount = models.IntegerField(default=1)


    @property
    def amount(self):
        return self._amount


    @amount.setter
    def amount(self, value):
        self._amount = int(value) if value >= 0 else 0
        self.save()


    def product_sum(self):
        product_sum = self.product.price * self.amount
        return product_sum