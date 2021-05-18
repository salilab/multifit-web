import unittest
import saliweb.test
import os
import re
from werkzeug.datastructures import FileStorage


# Import the multifit frontend with mocks
multifit = saliweb.test.import_mocked_frontend("multifit", __file__,
                                               '../../frontend')

def get_default_submit_parameters():
    return {'resolution': 4.0, 'spacing': 1.0, 'threshold': 0.1,
            'x_origin': 0.0, 'y_origin': 10.0, 'z_origin': 30.0,
            'cn_symmetry': 4}

class Tests(saliweb.test.TestCase):
    """Check submit page"""

    def test_submit_page(self):
        """Test submit page"""
        with saliweb.test.temporary_directory() as t:
            incoming = os.path.join(t, 'incoming')
            os.mkdir(incoming)
            multifit.app.config['DIRECTORIES_INCOMING'] = incoming
            c = multifit.app.test_client()
            rv = c.post('/job')
            self.assertEqual(rv.status_code, 400)  # no resolution
            self.assertIn(b'Map resolution input is missing or invalid.',
                          rv.data)

            data = get_default_submit_parameters()
            em_map = os.path.join(t, 'test.mrc')
            with open(em_map, 'w'):
                pass
            pdb = os.path.join(t, 'test.pdb')
            with open(pdb, 'w') as fh:
                fh.write(
                    "REMARK\n"
                    "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")

            # Successful submission (no email)
            data['map'] = open(em_map, 'rb')
            data['symm_pdb'] = open(pdb, 'rb')
            rv = c.post('/job', data=data)
            self.assertEqual(rv.status_code, 200)
            r = re.compile(b'Your job .* has been submitted.*'
                           b'Please see the job results.*'
                           b'You can check on your job.*'
                           b'If you experience any problems.*'
                           b'Thank you for using our server',
                           re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

    def _check_submit(self, data):
        with saliweb.test.temporary_directory() as t:
            incoming = os.path.join(t, 'incoming')
            os.mkdir(incoming)
            multifit.app.config['DIRECTORIES_INCOMING'] = incoming
            c = multifit.app.test_client()
            em_map = os.path.join(t, 'test.mrc')
            with open(em_map, 'w'):
                pass
            pdb = os.path.join(t, 'test.pdb')
            with open(pdb, 'w') as fh:
                fh.write(
                    "REMARK\n"
                    "ATOM      2  CA  ALA     1      26.711  14.576   5.091\n")
            data['map'] = open(em_map, 'rb')
            data['symm_pdb'] = open(pdb, 'rb')
            return c.post('/job', data=data)

    def test_submit_bad_spacing(self):
        """Test submit page with bad spacing"""
        data = get_default_submit_parameters()
        data['spacing'] = 'not-a-float'
        rv = self._check_submit(data)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Vector spacing input is missing or invalid.',
                      rv.data)


if __name__ == '__main__':
    unittest.main()
