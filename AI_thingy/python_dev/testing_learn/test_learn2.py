import unittest 
from unittest.mock import patch # we can use as a decorator or context manager..
import requests #4
from AI_thingy.python_dev.learn_testing.employee import Employee



# Note: test might not always run in order and ideally we should ensure all the tests are isolated 

# you can sometimes do - "Test Driven Developement" you write expected behavior code first and then the main code.. 

class TestEmployee(unittest.TestCase):

# -------------- #3 learn
# This is when you want something to run at first and then at the end.. eg; file creation -> we test everything -> delete the file.. we can use this.. 
    @classmethod
    def setUpClass(cls):
        print("setUp Class.. ")

    @classmethod
    def tearDownClass(cls):
        print("tearDown Class.. ")

# -------------- #2 learn: context_Managers
    #setup and teardown method: so we don't repeate variables again and again
    def setUp(self): #built-ins
        print("setUp..")
        self.emp1 = Employee('Adarsh', 'Shah', 70000)
        self.emp2 = Employee('Rohan', 'Sahu', 50000)
    def tearDown(self):
        # to tearDown the vars, and everything after test.. 

        # print(self.emp1.last)
        print("tearDown..\n")
        # pass


# -------------- #1 learn
    def test_email(self):

        # self.assertEqual(self.emp1.email, 'Adarsh.Shah@gmail.com') #no need now after setup and teardown..
        # self.assertEqual(self.emp2.email, 'Rohan.Sahu@gmail.com')

        self.emp1.first = 'Adarshhh' #changed just the first name
        self.emp2.first = 'Rohannn'
        self.assertEqual(self.emp1.email, 'Adarshhh.Shah@gmail.com')
        self.assertEqual(self.emp2.email, 'Rohannn.Sahu@gmail.com')

    def test_apply_raise(self):
        # self.emp1 = Employee('Adarsh', 'Shah', 70000)
        # self.emp2 = Employee('Rohan', 'Sahu', 50000) #it's repeatitive thus we'll find a better way..

        self.emp1.apply_raise()
        self.emp2.apply_raise() #now we want to ensure the raise is only by 5%

        self.assertEqual(self.emp1.pay, 73500)
        self.assertEqual(self.emp2.pay, 52500)

# ---------------#4 learn
    # say we're web requesting or scraping but the issue is from their side not out program so we don't want to flag our system thus use - 'mocking'

    def test_monthly_schedule(self):
        # we're using 'patch' as context manager
        # we're simulating the web request instead of acutal requests..
        with patch('employee.requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = '_Sucess_'

            schedule = self.emp1.monthly_schedule('May')

            # good things of mock objects is that we record when they are called and with what value - thus we can ensure what to calls with.. 
            mocked_get.assert_called_with('http://company.com/Shah/May')
            self.assertEqual(schedule, '_Sucess_')

            # testing failed resposne:
            mocked_get.return_value.ok = False
            schedule = self.emp2.monthly_schedule('June')
            mocked_get.assert_called_with('http://company.com/Sahu/June')
            self.assertEqual(schedule, '_Bad Response_')


if __name__ == '__main__':
    unittest.main()