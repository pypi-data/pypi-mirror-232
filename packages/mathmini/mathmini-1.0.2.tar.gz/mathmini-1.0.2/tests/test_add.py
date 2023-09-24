import unittest
from mathmini import add

class TestAdd(unittest.TestCase):

	def test_add(self):
		self.assertEqual(add(10, 5), 15)

if __name__ == '__main__':
    unittest.main()
