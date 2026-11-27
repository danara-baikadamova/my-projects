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

class Warrior(Hero):
    def __init__(self, name, hp, attack):
        super().__init__(name, hp, attack)

    def hit(self, enemy):
        enemy.hp -= self.attack 
        print(f"{self.name} атакует мечом {enemy.name}!")

class Mage(Hero):
    def __init__(self, name, hp, attack):
        super().__init__(name, hp, attack)

    def hit(self, enemy):
        enemy.hp -= self.attack * 2
        print(f"{self.name} атакует магией {enemy.name}!")

class Archer(Hero):
    def __init__(self, name, hp, attack):
        super().__init__(name, hp, attack)

    def hit(self, enemy):
        enemy.hp -= self.attack * 1.5
        print(f"{self.name} атакует стрелой {enemy.name}!")

warrior = Warrior("Knight", 100, 20)
mage = Mage("Wizard", 100, 15)
archer = Archer("Robin", 100, 18)

heroes = [warrior, mage, archer]

while sum(1 for h in heroes if h.hp > 0) > 1:
    for hero in heroes:
        if hero.hp <= 0:
            continue

        enemies = [h for h in heroes if h is not hero and h.hp > 0]

        if not enemies:
            break

        target = enemies[0]
        hero.hit(target)

        if target.hp <= 0:
            print(f"{target.name} погиб!")

print("\nРезультаты боя:")

for hero in heroes:
    if hero.hp > 0:
        print(hero.name, "победил!")
