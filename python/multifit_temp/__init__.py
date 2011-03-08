import saliweb.backend
import tarfile
import glob
import os
import re

class Job(saliweb.backend.Job):
    runnercls = saliweb.backend.SaliSGERunner

    def run(self):
        par = open('param.txt', 'r')
        resolution = float(par.readline().strip())
        spacing = float(par.readline().strip())
        threshold = float(par.readline().strip())
        x_origin = float(par.readline().strip())
        y_origin = float(par.readline().strip())
        z_origin = float(par.readline().strip())
        cn_symmetry = float(par.readline().strip())
        symmetry_mode = int(par.readline().strip())
        par.close()
        
        if symmetry_mode == 1:
            script = """
export IMP=/netapp/sali/multifit_temp/IMP
perl $IMP/modules/cn_multifit/bin/runMSPoints.pl input.pdb
$IMP/tools/imppy.sh python $IMP/modules/cn_multifit/bin/build_cn_multifit_params.py -- %d input.pdb input.map %f %f %f %f %f %f
$IMP/tools/imppy.sh $IMP/modules/cn_multifit/bin/symmetric_multifit multifit.param --chimera multifit.chimera.output
""" % (cn_symmetry, resolution, spacing, threshold, x_origin, y_origin, z_origin)

        else:
            script = """
export IMP=/netapp/sali/multifit_temp/IMP
perl $IMP/modules/cn_multifit/bin/runMSPoints.pl input.pdb
$IMP/tools/imppy.sh python $IMP/modules/multifit2/bin/generate_assembly_input.py input.subunit.list.txt %s input.map %f %f 500 %f %f %f 
""" % (resolution, spacing, threshold, x_origin, y_origin, z_origin)

        script += """
mkdir asmb_models
cp asmb.model.*.pdb asmb_models
tar cf asmb_models.tar asmb_models
gzip -9 asmb_models.tar
rm -rf asmb_models
"""
        r = self.runnercls(script)
        r.set_sge_options('-l o64=true -l diva1=1G')
        return r

    def postprocess(self):
        self.generate_image_thumbnail()
        self.generate_all_chimerax()

    def generate_image_thumbnail(self): 
        output_pdbs = glob.glob('asmb.model.*.pdb')
        size = "50x50"
        
        for pdb_in in output_pdbs:
            (filename, extension) = os.path.splitext(pdb_in)
            jpg_out = filename + ".jpg"
            molscriptin = "/usr/local/bin/molauto %s -r 2> /dev/null \
                         | /usr/local/bin/molscript -r 2> /dev/null \
                         | /usr/bin/render -size %s -jpeg > %s" % (pdb_in, size, jpg_out) 
            os.system (molscriptin)

    def generate_all_chimerax(self): 
        output_pdbs = glob.glob('asmb.model.*.pdb')

        for pdb_in in output_pdbs:
            self.generate_chimerax(pdb_in, False)
        #self.generate_chimerax("asmb.model.0.pdb", True) #chimerax with density map and PDB structure

    # Generate Chimera web data (chimerax) files
    def generate_chimerax(self, pdb_in, include_map_flag): 
        (filepath, jobdir) = os.path.split(self.url)
        pdb_temp = "/" + pdb_in + "?"
        pdb_url = re.sub('\?', pdb_temp, jobdir)
        full_path = filepath + "/" + pdb_url

        (filename, extension) = os.path.splitext(pdb_in)
        chimerax_out = filename + ".chimerax"
        if include_map_flag:
            chimerax_out = filename + ".map.chimerax"
            map_temp = "/" + "input.map" + "?"
            map_url = re.sub('\?', map_temp, jobdir)
            map_path = filepath + "/" + map_url

        infile = open(chimerax_out, 'w')
        print >> infile, "<?xml version=\"1.0\"?>"
  	print >> infile, "<ChimeraPuppet type=\"std_webdata\">"
  	print >> infile, "<web_files>"
  	print >> infile, "   <file  name=\"%s\" format=\"text\" loc=\"%s\" />" %(pdb_in, full_path)
        if include_map_flag:
  	    print >> infile, "   <file  name=\"input.map\" format=\"mrc\" loc=\"%s\" />" %(map_path)
  	print >> infile, "</web_files>"
  	print >> infile, """
<commands>
    <py_cmd>model = chimera.openModels.list()[0]</py_cmd>
    <mid_cmd>ribbon</mid_cmd>
    <mid_cmd>~disp</mid_cmd>
    <mid_cmd>modelcolor #fa8072 #0</mid_cmd>
    <mid_cmd>ribrepr smooth</mid_cmd>
"""
        if include_map_flag:
            print >> infile, "    <mid_cmd>vol all transparency 0.5</mid_cmd>"
            print >> infile, "    <mid_cmd>vol all level 0.825</mid_cmd>"
        print >> infile, "</commands>"
        print >> infile, "</ChimeraPuppet>"
        infile.close()

    def archive(self):
        output_pdbs = glob.glob('*.pdb')
        t1 = tarfile.open('output-pdbs.tar.bz2', 'w:bz2')
        for pdb in output_pdbs:
            t1.add(pdb)
        t1.close()
        for pdb in output_pdbs:
            os.unlink(pdb)

        output_jpgs = glob.glob('*.jpg')
        t2 = tarfile.open('output-jpgs.tar.bz2', 'w:bz2')
        for jpg in output_jpgs:
            t2.add(jpg)
        t2.close()
        for jpg in output_jpgs:
            os.unlink(jpg)

        output_chimerax = glob.glob('*.chimerax')
        t3 = tarfile.open('output-chimerax.tar.bz2', 'w:bz2')
        for chimerax in output_chimerax:
            t2.add(chimerax)
        t3.close()
        for jpg in output_chimerax:
            os.unlink(chimerax)

def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = saliweb.backend.Config(config_file)
    return saliweb.backend.WebService(config, db)
