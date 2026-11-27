class Hero:
    def __init__(self, name, hp, attack):
        self.name = name
        self.hp = hp
        self.attack = attack

    def hit(self, enemy):
        enemy.hp -= self.attack
        print(f"{self.name} атакует {enemy.name}!")
        print(f"У {enemy.name} осталось {enemy.hp} HP")

    def __str__(self):
        return f"{self.name}: HP = {self.hp}, Attack = {self.attack}"


hero1 = Hero("Knight", 100, 20)
hero2 = Hero("Dragon", 100, 15)

print(hero1)
print(hero2)

while hero1.hp > 0 and hero2.hp > 0:
    hero1.hit(hero2)

    if hero2.hp <= 0:
        break

    hero2.hit(hero1)

print("Конец боя!")

if hero1.hp > 0:
    print(hero1.name, "победил!")
else:
    print(hero2.name, "победил!")