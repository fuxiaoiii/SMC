def a1():
    global a
    a=2
    print("In test_function, before modification, a is:", a)  # 可以在函数中访问全局变量 a
    a=4

def a2():
    global a
    a=5
    print("In test_function2, after modification, a is:", a)


if __name__ == "__main__":

    a1()
    a2()
