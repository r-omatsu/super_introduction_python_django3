in_str = input('type a number:')
num = int(in_str)
total = 0
for n in range(num + 1):
    total += n
print(in_str + 'までの合計は、' + str(total) + 'です。')
