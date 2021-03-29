class Member:
    name = 'no name'
    age = 0
    mail = 'no address'

    def __init__(self, name='no name', age=0, mail='no address'):
        self.name = name
        self.age = age
        self.mail = mail

    def print(self):
        print(self.name + '(' + str(self.age) + ' old. ' + self.mail + ')')

class Employee(Member):
    company = 'unemployed'

    def __init__(self, company='', name='no name', age=0, mail='no address'):
        self.company = company
        super().__init__(name, age, mail)

    def print(self):
        print(self.name + '(' + str(self.age) + ' old. ' + self.mail + '[' + self.company + '])')


taro = Member('Taro-Yamada', 39, 'taro@yamada.kun')
taro.print()
hanako = Employee(name='Hanako-Tanaka', mail='hanako@flower.san', company='test system')
hanako.print()
