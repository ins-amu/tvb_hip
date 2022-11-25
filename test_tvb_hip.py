import unittest

class TestSite(unittest.TestCase):

    def test_fs(self):
        "Test we can find FreeSurfer on $PATH"
        self.assertFalse(1)

    def test_flirt(self):
        "Test we can use flirt."
        self.assertFalse(1)

    def test_mrconvert(self):
        "Test we can use mrconvert."
        self.assertFalse(1)

def run_all_tests():
    unittest.main()

if __name__ == '__main__':
    run_all_tests()
