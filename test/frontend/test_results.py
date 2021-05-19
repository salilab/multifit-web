import unittest
import saliweb.test
import re

# Import the multifit frontend with mocks
multifit = saliweb.test.import_mocked_frontend("multifit", __file__,
                                               '../../frontend')


def get_output():
    return """solution index | solution filename | fit rotation | fit translation  | match size | match average distance |  envelope penetration score | fitting score|dock rotation | dock translation | RMSD to reference
0|asmb.model.0.pdb|0.0337689 -0.00835729 0.0018406 -0.999393|43.7796 85.915 84.2254|0|-1|-1|0.0854502|0.900969 -0.00756934 0.00111879 -0.433816|-18.3563 -30.6263 0.241108|-1
2|asmb.model.1.pdb|0.0840649 0.0815502 0.0090198 -0.993077|33.9721 88.0333 84.2464|0|-1|-1|0.163918|0.900969 0.0704937 0.00114512 -0.428117|-27.4183 -34.4749 -4.60705|-1
"""  # noqa: E501


class Tests(saliweb.test.TestCase):
    """Check results page"""

    def test_mime_type(self):
        """Test MIME type"""
        self.assertEqual(multifit.get_mime_type('asmb.model.0.chimerax'),
                         'application/x-chimerax')
        self.assertEqual(multifit.get_mime_type('asmb.model.0.pdb'),
                         'chemical/x-pdb')
        self.assertEqual(multifit.get_mime_type('multifit.output'),
                         'text/plain')
        self.assertIsNone(multifit.get_mime_type('multifit.foo'))

    def test_results_file(self):
        """Test download of results files"""
        with saliweb.test.make_frontend_job('testjob') as j:
            j.make_file('multifit.log')
            j.make_file('not-allowed.log')
            c = multifit.app.test_client()
            rv = c.get('/job/testjob/multifit.log?passwd=%s' % j.passwd)
            self.assertEqual(rv.status_code, 200)
            rv = c.get('/job/testjob/not-allowed.log?passwd=%s' % j.passwd)
            self.assertEqual(rv.status_code, 404)

    def test_failed_job(self):
        """Test display of failed job"""
        with saliweb.test.make_frontend_job('testjob3') as j:
            c = multifit.app.test_client()
            rv = c.get('/job/testjob3?passwd=%s' % j.passwd)
            r = re.compile(
                b'Your MultiFit job.*testjob3.*failed to produce any '
                b'output models.*For more information, '
                rb'you can download the.*multifit\.log.*MultiFit log file.*'
                b'contact us',
                re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)

    def test_ok_job(self):
        """Test display of OK job"""
        with saliweb.test.make_frontend_job('testjob4') as j:
            j.make_file("multifit.output", contents=get_output())
            c = multifit.app.test_client()
            rv = c.get('/job/testjob4?passwd=%s' % j.passwd)
            r = re.compile(
                b'Job .*testjob4.*has completed.*'
                rb'asmb\.model\.0\.chimerax\?passwd=pwgoodcrypt.*'
                rb'asmb\.model\.0\.jpg\?passwd=pwgoodcrypt.*'
                rb'asmb\.model\.0\.pdb\?passwd=pwgoodcrypt.*'
                rb'asmb\.model\.0\.pdb.*'
                b'CC score=0.9.*'
                rb'Download.*multifit\.output.*'
                rb'asmb_models\.tar\.gz\?passwd=pwgoodcrypt.*'
                b'Job results will be available',
                re.MULTILINE | re.DOTALL)
            self.assertRegex(rv.data, r)


if __name__ == '__main__':
    unittest.main()
