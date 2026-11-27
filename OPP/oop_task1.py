class User:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age

    def show_info(self):
        return f"Имя: {self.name}, Email: {self.email}, Возраст: {self.age}"

    def __str__(self):
        return f"Пользователь: {self.name}, {self.email}"

class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def calculate_total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Товар: {self.name}, Цена: {self.price} тг."

class Order:
    def __init__(self, order_id, user, product):
        self.order_id = order_id
        self.user = user
        self.product = product

    def show_order(self):
        return f"Заказ №{self.order_id}: {self.user.name} заказал {self.product.name}"

    def __str__(self):
        return f"Заказ №{self.order_id} от пользователя {self.user.name}"

#создание обьектов
user1 = User("danara", "danara@gmail.com", 15)
product1 = Product("телефон", 50000, 1)
order1 = Order(101, user1, product1)

#вывод информации
print(user1)
print(user1.show_info())

print(product1)
print(f"Общая стоимость: {product1.calculate_total_price()} тг.")

print(order1)
print(order1.show_order())