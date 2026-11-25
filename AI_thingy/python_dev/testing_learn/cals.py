#  this is a revision on creating tests to ensure a structual and systemic integrity of your project to ensure that it's not causing the errors we alredy enticipare.. it's the pytest we usually have done till now.. 

def add(x,y):
    return x + y

def sub(x,y):
    return x - y

def multiply(x,y):
    return x*y #delibrate mistake to see how test help us quickly resolve silly mistakes..

def div(x,y):
    if y==0:
        raise ValueError('Undefined')
    return x/y


if __name__ == '__main__':
    print(add(3,5))