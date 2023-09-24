import unittest
from mathmini import sub

class TestSub(unittest.TestCase):

	def test_sub(self):
		self.assertEqual(sub(10, 5), 5)

if __name__ == '__main__':
    unittest.main()
