import requests

class Employee:
    raise_amt = 1.05

    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay 

    @property
    def email(self):
        return '{}.{}@gmail.com'.format(self.first, self.last) #automatic name change in the email.. 

    @property
    def fullname(self):
        return '{} {}'.format(self.first, self.last)

    def apply_raise(self):
        self.pay = int(self.pay * self.raise_amt) #adjust the pay according to the raise.. 

    def monthly_schedule(self, month='May'):
        response = requests.get(f'http://company.com/{self.last}/{month}')
        if response.ok:
            return response.text
        else:
            return '_Bad Response_'

if __name__ == '__main__':
    print("running.. ")