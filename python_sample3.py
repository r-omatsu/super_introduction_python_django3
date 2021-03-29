def check(num):
    if int(num) % 2 == 0:
        return '偶数'
    else:
        return '奇数'

n = input('整数を入力:')
print(str(n) + 'は、' + check(n) + ' ! ')
