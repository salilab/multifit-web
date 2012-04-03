import unittest
import multifit
import saliweb.backend
import saliweb.test
import tarfile
import os
import re

class PostProcessTests(saliweb.test.TestCase):
    """Check postprocessing functions"""

    def test_archive(self):
        """Test archive function"""
        # Make a Multifit Job test job in ARCHIVED state
        j = self.make_test_job(multifit.Job, 'ARCHIVED') 
        # Run the rest of this testcase in the job's directory
        d = saliweb.test.RunInDir(j.directory)
        # Make test PDB and JPG files and another incidental file
        in_files = ['test1.pdb', 'test2.pdb', 'test1.jpg', 'test2.jpg']
        for f in in_files:
            print >> open(f, 'w'), "test file"
        print >> open('test.txt', 'w'), "text file"

        j.archive()

        # Original PDB and JPG files should have been deleted
        for f in in_files:
            self.assertEqual(os.path.exists(f), False)
        tar = tarfile.open('output-pdbs.tar.bz2', 'r:bz2')
        self.assertEqual(sorted([p.name for p in tar]),
                         ['test1.pdb', 'test2.pdb'])
        self.assertTrue(os.path.exists('test.txt'))
        tar.close()
        tar = tarfile.open('output-jpgs.tar.bz2', 'r:bz2')
        self.assertEqual(sorted([p.name for p in tar]),
                         ['test1.jpg', 'test2.jpg'])
        tar.close()
        os.unlink('output-pdbs.tar.bz2')
        os.unlink('output-jpgs.tar.bz2')

    def assert_file_contents_re(self, fname, regex):
        contents = open(fname).read()
        self.assert_(re.search(regex, contents, re.MULTILINE | re.DOTALL),
                     "Contents of file %s (%s) do not match regex %s" \
                     % (fname, contents, regex))

    def assert_re(self, txt, regex):
        self.assert_(re.search(regex, txt),
                     "Text %s does not match regex %s" % (txt, regex))

    def test_postprocess(self):
        """Test postprocess method"""
        j = self.make_test_job(multifit.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        # Make sure that expected methods were called
        calls = []
        class MockMethod(object):
            def __init__(self, name):
                self.name = name
            def __call__(self):
                calls.append(self.name)
        old_thumb = multifit.Job.generate_image_thumbnail
        old_gen = multifit.Job.generate_all_chimerax
        try:
            multifit.Job.generate_image_thumbnail = MockMethod('thumbnail')
            multifit.Job.generate_all_chimerax = MockMethod('chimerax')
            j.postprocess()
        finally:
            multifit.Job.generate_image_thumbnail = old_thumb
            multifit.Job.generate_all_chimerax = old_gen
        self.assertEqual(calls, ['thumbnail', 'chimerax'])

    def test_generate_all_chimerax(self):
        """Test generate_all_chimerax method"""
        j = self.make_test_job(multifit.Job, 'RUNNING')
        d = saliweb.test.RunInDir(j.directory)
        open('asmb.model.0.pdb', 'w')
        open('asmb.model.1.pdb', 'w')
        calls = []
        def dummy_generate(self, pdb, flag):
            calls.append((pdb, flag))
        old_generate = multifit.Job.generate_chimerax
        try:
            multifit.Job.generate_chimerax = dummy_generate
            j.generate_all_chimerax()
        finally:
            multifit.Job.generate_chimerax = old_generate
        self.assertEqual(calls, [('asmb.model.0.pdb', False),
                                 ('asmb.model.1.pdb', False)])

    def test_generate_image_thumbnail(self):
        """Test generate_image_thumbnail method"""
        j = self.make_test_job(multifit.Job, 'RUNNING') 
        d = saliweb.test.RunInDir(j.directory)
        open('asmb.model.0.pdb', 'w')
        open('asmb.model.1.pdb', 'w')
        cmds = []
        def mock_system(cmd):
            cmds.append(cmd)
        old_system = os.system
        try:
            os.system = mock_system
            j.generate_image_thumbnail()
        finally:
            os.system = old_system
        self.assertEqual(len(cmds), 2)
        for i in range(2):
            self.assert_re(cmds[i],
                      'molauto asmb\.model\.%d\.pdb .*molscript \-r .*'
                      'render \-size 50x50 \-jpeg > asmb\.model\.%d\.jpg' \
                      % (i, i))

    def test_generate_chimerax(self):
        """Test generate_chimerax method"""
        j = self.make_test_job(multifit.Job, 'RUNNING') 
        d = saliweb.test.RunInDir(j.directory)

        os.mkdir('test1')
        j.generate_chimerax('test1/test.pdb', False)
        self.assert_file_contents_re('test1/test.chimerax',
                 '<ChimeraPuppet .*<file\s+name="test1/test\.pdb" '
                 '.*loc="http:.*testjob\/test1\/test\.pdb\?passwd=abc".*'
                 '</ChimeraPuppet>')
        os.unlink('test1/test.chimerax')
        os.rmdir('test1')

        os.mkdir('test2')
        j.generate_chimerax('test2/foo.pdb', True)
        self.assert_file_contents_re('test2/foo.map.chimerax',
                 '<ChimeraPuppet .*<file\s+name="test2/foo\.pdb" '
                 '.*loc="http:.*testjob\/test2\/foo\.pdb\?passwd=abc".*'
                 '<file\s+name="input\.mrc"'
                 '.*loc="http://.*testjob\/input\.mrc\?passwd=abc".*'
                 '</ChimeraPuppet>')
        os.unlink('test2/foo.map.chimerax')
        os.rmdir('test2')

if __name__ == '__main__':
    unittest.main()
