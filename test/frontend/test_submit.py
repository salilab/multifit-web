import unittest
import saliweb.test
import os
import re


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

    def _check_submit(self, data, input_map='default', input_pdb='default',
                      with_atom=True):
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
                    "REMARK\n")
                if with_atom:
                    fh.write("ATOM      2  CA  ALA     1      "
                             "26.711  14.576   5.091\n")
            if input_map == 'default':
                data['map'] = open(em_map, 'rb')
            else:
                data['map'] = input_map
            if input_pdb == 'default':
                data['symm_pdb'] = open(pdb, 'rb')
            else:
                data['symm_pdb'] = input_pdb
            return c.post('/job', data=data)

    def test_submit_bad_spacing(self):
        """Test submit page with bad spacing"""
        data = get_default_submit_parameters()
        data['spacing'] = 'not-a-float'
        rv = self._check_submit(data)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Vector spacing input is missing or invalid.',
                      rv.data)

    def test_submit_bad_cn_symmetry(self):
        """Test submit page with cn_symmetry"""
        for sym in ('not-an-integer', '2'):
            data = get_default_submit_parameters()
            data['cn_symmetry'] = sym
            rv = self._check_submit(data)
            self.assertEqual(rv.status_code, 400)
            self.assertIn(b'Cn symmetry should be an integer',
                          rv.data)

    def test_submit_bad_threshold(self):
        """Test submit page with bad threshold"""
        data = get_default_submit_parameters()
        data['threshold'] = 'not-a-float'
        rv = self._check_submit(data)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Contour level input is missing or invalid.',
                      rv.data)

    def test_submit_bad_origin(self):
        """Test submit page with bad origin"""
        for field in ('x_origin', 'y_origin', 'z_origin'):
            data = get_default_submit_parameters()
            data[field] = 'not-a-float'
            rv = self._check_submit(data)
            self.assertEqual(rv.status_code, 400)
            self.assertIn(b'Origin input is invalid.',
                          rv.data)

    def test_submit_no_mrc(self):
        """Test submit page with no density file"""
        data = get_default_submit_parameters()
        rv = self._check_submit(data, input_map=None)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Please upload input density map.',
                      rv.data)

    def test_submit_no_pdb(self):
        """Test submit page with no PDB"""
        data = get_default_submit_parameters()
        rv = self._check_submit(data, input_pdb=None)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Please select upload subunit PDB',
                      rv.data)

    def test_submit_pdb_no_atom(self):
        """Test submit page with PDB containing no atoms"""
        data = get_default_submit_parameters()
        rv = self._check_submit(data, with_atom=False)
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'PDB file contains no ATOM records',
                      rv.data)


if __name__ == '__main__':
    unittest.main()
