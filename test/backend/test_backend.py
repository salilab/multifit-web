import unittest
import multifit
import saliweb.backend
import saliweb.test
import tarfile
import os

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

if __name__ == '__main__':
    unittest.main()
