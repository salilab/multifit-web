import unittest
import saliweb.test

# Import the multifit frontend with mocks
multifit = saliweb.test.import_mocked_frontend("multifit", __file__,
                                               '../../frontend')


class Tests(saliweb.test.TestCase):

    def test_index(self):
        """Test index page"""
        c = multifit.app.test_client()
        rv = c.get('/')
        self.assertIn(b'Fitting of multiple proteins into their assembly',
                      rv.data)

    def test_contact(self):
        """Test contact page"""
        c = multifit.app.test_client()
        rv = c.get('/contact')
        self.assertIn(b'Please address inquiries to', rv.data)

    def test_help(self):
        """Test help page"""
        c = multifit.app.test_client()
        rv = c.get('/help')
        self.assertIn(b'symmetry example in building a chaperon ring', rv.data)

    def test_queue(self):
        """Test queue page"""
        c = multifit.app.test_client()
        rv = c.get('/job')
        self.assertIn(b'No pending or running jobs', rv.data)


if __name__ == '__main__':
    unittest.main()
