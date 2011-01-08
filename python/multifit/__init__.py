import saliweb.backend
import glob
import gzip
import os

class Job(saliweb.backend.Job):
    runnercls = saliweb.backend.SaliSGERunner

    def run(self):
        par = open('param.txt', 'r')
        resolution = float(par.readline().strip())
        spacing = float(par.readline().strip())
        density_threshold = float(par.readline().strip())
        cn_symmetry = float(par.readline().strip())
        par.close()
        
        script = """
export MULTIFIT=/netapp/sali/multifit/IMP/modules/multifit
export IMP=/netapp/sali/multifit/IMP
perl $IMP/modules/cn_multifit/bin/runMSPoints.pl input.pdb
python $IMP/modules/cn_multifit/bin/build_cn_multifit_params.py -- %d input.pdb input.map %f %f %f  -130.5  -84 -87
$IMP/tools/imppy.sh $IMP/modules/cn_multifit/bin/cn_multifit_main multifit.param
""" % (cn_symmetry, resolution, spacing, density_threshold)

        r = self.runnercls(script)
        r.set_sge_options('-l o64=true -l diva1=1G')
        return r

    def archive(self):
        for f in glob.glob('*.pdb'):
            fin = open(f, 'rb')
            fout = gzip.open(f + '.gz', 'wb')
            fout.writelines(fin)
            fin.close()
            fout.close()
            os.unlink(f)

def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = saliweb.backend.Config(config_file)
    return saliweb.backend.WebService(config, db)
