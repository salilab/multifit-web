import unittest
import multifit_temp
import saliweb.backend
import saliweb.test
import tarfile
import os

class PostProcessTests(saliweb.test.TestCase):
    """Check postprocessing functions"""

    def test_archive(self):
        """Test archive function"""
        # Make a Multifit Job test job in ARCHIVED state
        j = self.make_test_job(multifit_temp.Job, 'ARCHIVED') 
        # Run the rest of this testcase in the job's directory
        d = saliweb.test.RunInDir(j.directory)
        # Make test PDB files and another incidental file
        in_pdbs = ['test1.pdb', 'test2.pdb']
        for pdb in in_pdbs:
            print >> open(pdb, 'w'), "test pdb"
        print >> open('test.txt', 'w'), "text file"

        j.archive()

        # Original PDB files should have been deleted
        for pdb in in_pdbs:
            self.assertEqual(os.path.exists(pdb), False)
        tar = tarfile.open('output-pdbs.tar.bz2', 'r:bz2')
        self.assertEqual(sorted([p.name for p in tar]), in_pdbs)
        self.assertTrue(os.path.exists('test.txt'))
        tar.close()
        os.unlink('output-pdbs.tar.bz2')

if __name__ == '__main__':
    unittest.main()
