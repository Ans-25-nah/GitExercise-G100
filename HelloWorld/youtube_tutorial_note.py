# this is just a note,python and pygame learning note
# just for me to remember what i have learned

# 1.FUNDAMENTAL OF PYTHON：python 语法

# 1)variables 变量
# 设x=1之类的
# 可以设整数int，小数点float，string，booleans
student_count = 1000
print("student_count")

# 2)variable names 名字的规则
# a)不可以用数字开头
# b)不可以有空格，只可以用_来隔开
# c)不可以用true false等，电脑已经设置好的字
# d)小字母
# e)描述很清晰的那种

# 3)string
course = "Python for Beginners"

print(course)
print(len(course))
print(course[0])
print(course[-1])  # 后面开始
print(course[0:3])  # 第一个开始到第四个之前
print(course[0:])
print(course[:3])
print(course[:])

# 4)escape sequences \
study = "python\"programming\"thing"
# \"
# \n
# \'
# \\
print(study)  # python"programming"thing

# 5)formatted strings
# full=f"{ } { }"

first = "dang"
last = "yee ting"
full = f"{len(first)} {2+2}"
print(full)


# 6)string methods:add . upper大字母/lower小字母/title标题/stripy去掉空格 after name
# lstrip 左边空格去掉，rstrip 右边空格去掉
course = "Python programming"
print(course.upper())
print(course.lower())
print(course.title())
print(course.strip())
print(course.find("pro"))  # 一定要跟着小字母，如果是大字母，电脑会找不到
print(course.replace("p", "j"))  # p替换成j
print("pro" in course)  # 答案会是true
print("swift" not in course)  # 答案也是true

# 7)number
print(10+3)
print(10-3)
print(10*3)
print(10/3)  # 正常除
print(10//3)  # 只剩下商数，去掉余数
print(10 % 3)  # 只剩下余数，去掉商数
print(10**3)  # 次方 10^3

# ori
x = 10
x = x+3  # 10+3=13
print(x)  # x=13

# pro
y = 10
y += 3  # 10+3=13
print(y)  # y=13

# 还可以有-=，*=....

# useful function Working with numbers

print(round(2.9))  # 四舍五入
print(abs(-2.9))  # 绝对值
# 如果round和abs不够用，可以代入math 模版
# 在代码的最顶端写上import math，就可以调用ceil（向上取整）/floor（向下取整）

# 8)type conversion 类型转换
# 当我们使用input(),无论输入什么，电脑都会看成string
# therefore 我们需要转换
# int(x) 整数
# float(x) 小数点
# bool(x) boolean：true/false
# str(x) string
input("x: ")
y = int(x)+1
print(f"x:{x},y:{y}")

# FUNDAMENTAL OF PROGRAMMING

# 1)comparison operators 比较运算
# 比较两个数据的大小&状态
print(10 > 3)
print(10 < 3)
print(10 >= 3)  # 大于等于
print(10 <= 3)  # 小于等于
print(10 == 3)  # 互相等于
print(10 != 3)  # 不等于

# 2）conditional statements
# if 如果
# elif 又或者
# else 如果不是

temperature = 35
if temperature > 30:
    print("It's warm")  # 一定是空几个格子
    print("Drink water")
elif temperature > 20:  # 和if一样格子
    print("It's cold")
print("Done")

# 3)ternary operator
# if-else的极简版
# if-else version
age = 22
if age >= 18:
    message = "adult"
else:
    message = "child"
print(message)

# if-else pro version
# [条件成立时的值]  if  [条件]  else  [条件不成立时的值]
message = "Adult" if age >= 18 else "child"
print(message)

# 4)logical operators :or and not
# not:1=0/0=1
# or:all 0=0
# and:all 1=1

has_high_income = True
has_good_credit = True

if has_high_income and has_good_credit:  # all 1=1 才print
    print("Eligible for loan")

has_high_income = False
has_good_credit = True

# 因为有好的信用记录（为 True），虽然收入不高（为 False），结果依然是 True
if has_high_income or has_good_credit:
    print("Eligible for loan")

has_good_credit = True
has_criminal_record = False

# 我们需要他“有良好信用”，并且“没有犯罪记录”
if has_good_credit and not has_criminal_record:
    print("Eligible for loan")


# 5)short-circuit evaluations 短路机制
# or：如果第一条件为true就直接判定为true，不看后面的东西
# and:如果聪明看到第一条件是false就直接判定为false，不看后面的东西


# 6)chaining comparison operators
# 可以吧多个比较条件直接连在一起写

# ori
age = 22

# 必须写两遍 age 变量
if age >= 18 and age < 65:
    print("Eligible")

# chain
age = 22

# 完美的链式比较！
if 18 <= age < 65:
    print("Eligible")


# 7)For..Else


successful = False  # 假设网络断开了

for attempt in range(3):
    print("Attempting to connect...")

    if successful:
        print("Connected successfully!")
        break  # 一旦连接成功，立刻打断循环，不再重试！

# 这个 else 是和 for 对齐的，而不是和 if 对齐！
else:
    # 只有当循环老老实实跑完 3 次，都没有触发上面的 break 时，才会来到这里
    print("Attempted 3 times and failed.")

#  8)Nested Loops
# 外层循环（Outer Loop） 就像是时针。
# 内层循环（Inner Loop） 就像是分针。
# 时针（外层）每走 1 格，分针（内层）就必须完完整整地跑完 60 格。只有当分针跑完了一整圈，时针才会往下走第 2 格。
# 外层循环每执行一次，内层循环都要从头到尾完整地执行一遍。

for x in range(3):        # 外层循环：x 会分别是 0, 1, 2
    for y in range(2):    # 内层循环：y 会分别是 0, 1
        print(f"({x}, {y})")

        # 外层第 1 步： 电脑先看外层，拿到 x = 0。然后走进内层。
        # 内层开始跑：拿到 y = 0，打印 (0, 0)
        # 内层继续跑：拿到 y = 1，打印 (0, 1)
        # 内层的 2 次跑完了，退出内层。
        # 外层第 2 步： 电脑回到外层，拿到 x = 1。再次走进内层。
        # 内层重新开始跑：拿到 y = 0，打印 (1, 0)
        # 内层继续跑：拿到 y = 1，打印 (1, 1)
        # 内层又跑完了，再次退出。
        # 外层第 3 步： 电脑回到外层，拿到 x = 2。最后一次走进内层。
        # 内层重新开始跑：拿到 y = 0，打印 (2, 0)
        # 内层继续跑：拿到 y = 1，打印 (2, 1)
        # 执行结束后，你的屏幕上会整齐地打印出 6 行坐标。

#  9)Iterables

#  10)While Loops
# 只要满足某个条件（结果为 True），就一直不停地重复执行代码；一旦条件不满足（变成 False）了，立刻停手退出。”
# 用于不知道要循环多少次，你只知道“达到什么目标就可以停下”时

number = 1

# 电脑判断：1 小于等于 5 吗？是的 (True)，进入循环
while number <= 5:
    print(number)
    # ⚠️ 这一步极其关键：更新状态！
    number = number + 1


#  11)Infinite Loops

#  12)Defining Functions

# 13)Arguments

# 14)Types of Functions

# 15)Keyword Arguments

# 16)Default Arguments

# 17)xargs
