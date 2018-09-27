# 定义第一个装饰器
def set_func1(func):
    def wrappert(*args, **kwargs):
        print("要开始执行的语句1")
        func(*args, **kwargs)
        print("要结束执行的语句1")

    return wrappert


# 定义第二个装饰器
def set_func2(func):
    def wrappert(*args, **kwargs):
        print("要开始执行的语句2")
        func(*args, **kwargs)
        print("要结束执行的语句2")

    return wrappert


@set_func1
@set_func2
def show1():
    print("hell python")


show1()
"""
执行过程：
    show = set_func2(show)
    @set_func1
    def wrapper2
    
wrapper2 = set_func1(wrapper2)---->wrapper1
show = wrapper1
show = set_func1.wrapper(set_func2.wrapper2(show))
show()
"""