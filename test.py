import time

a_list = ['0']
b_list = ['1', '4']

b_list += a_list

print(time.asctime(time.localtime(time.time())))
