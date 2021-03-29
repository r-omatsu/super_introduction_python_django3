class Calc:
    tax = 0.1

    @classmethod
    def calc(cls, price):
        res = price * (1.0 + cls.tax) // 1.0
        print(str(price) + '円の税込価格は、' + str(res) + '円。')

Calc.calc(12300)
Calc.tax = 0.08
Calc.calc(12300)
