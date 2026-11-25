import unittest
import cals as cals 

# ref to doc: https://www.youtube.com/redirect?event=video_description&redir_token=QUlxb01IYWF5NDNvcGNFSExtcXdmSVNRMjVrMXxBQnJ0NjlsaG8yX0hvTmFGbk1HMWpkUkx0SG0zYkstUHg2MTJFX1JkZEhPdDRKN3VSLXFtUWZQa3BXbnZKUHk2MUtxOWg1RGRYOEhsczl5aHpDNnVHNVRMbkd2bGxza1NtZ0RM&q=https%3A%2F%2Fdocs.python.org%2F3%2Flibrary%2Funittest.html%23unittest.TestCase.debug&v=6tNS--WetLI

class TestCals(unittest.TestCase):

    def test_add(self): #prefix: 'test_' + 'add or whatever' -> counts as one test
        # result = cals.add(10,5)
        self.assertEqual(cals.add(10,5), 15) #match with what we're expecting..
        self.assertEqual(cals.add(-10,5), -5) #testing edge cases..
        self.assertEqual(cals.add(-1,1), 0) 
        self.assertEqual(cals.add(-1,-1), -2) 

    def test_sub(self): #prefix: 'test_' + 'sub or whatever' -> counts as one test
        # result = cals.sub(10,5)
        self.assertEqual(cals.sub(10,5), 5) #match with what we're expecting..
        self.assertEqual(cals.sub(-10,5), -15) #testing edge cases..
        self.assertEqual(cals.sub(-1,1), -2) 
        self.assertEqual(cals.sub(-1,-1), 0) 

    def test_multiply(self): #prefix: 'test_' + 'multiply or whatever' -> counts as one test
        # result = cals.multiply(10,5)
        self.assertEqual(cals.multiply(10,5), 50) #match with what we're expecting..
        self.assertEqual(cals.multiply(-10,5), -50) #testing edge cases..
        self.assertEqual(cals.multiply(-1,1), -1) 
        self.assertEqual(cals.multiply(-1,-1), 1) 

    def test_div(self): #prefix: 'test_' + 'div or whatever' -> counts as one test
        # result = cals.div(10,5)
        self.assertEqual(cals.div(10,5), 2) #match with what we're expecting..
        self.assertEqual(cals.div(-10,5), -2) #testing edge cases..
        self.assertEqual(cals.div(-1,1), -1) 
        self.assertEqual(cals.div(-1,-1), 1) 
        self.assertEqual(cals.div(5,2), 2.5) 

        # self.assertRaises(ValueError, cals.div, 5, 0) #to reproduce predictable errors.. ideally: error, function_name, parameters, 

        with self.assertRaises(ValueError):
            cals.div(5,0)


if __name__ == "__main__":
#     # print(cals.add(5,5))
    unittest.main()
