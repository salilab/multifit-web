from __future__ import print_function
import saliweb.backend
import tarfile
import glob
import os
import re
import subprocess


class Job(saliweb.backend.Job):
    runnercls = saliweb.backend.WyntonSGERunner

    def run(self):
        par = open('param.txt', 'r')
        resolution = float(par.readline().strip())
        spacing = float(par.readline().strip())
        threshold = float(par.readline().strip())
        x_origin = float(par.readline().strip())
        y_origin = float(par.readline().strip())
        z_origin = float(par.readline().strip())
        cn_symmetry = float(par.readline().strip())
        par.close()

        script = """
module load Sali
module load imp
cnmultifit surface input.pdb
cnmultifit param -n 20 -- %d input.pdb input.mrc %f %f %f %f %f %f
cnmultifit build multifit.param
sleep 10
mkdir asmb_models
cp asmb.model.*.pdb asmb_models
tar cf asmb_models.tar asmb_models
gzip -9 asmb_models.tar
rm -rf asmb_models
""" % (cn_symmetry, resolution, spacing, threshold, x_origin, y_origin,
                z_origin)

        r = self.runnercls(script)
        r.set_sge_options('-l h_rt=72:00:00 -j y -o multifit.log')
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
            molscriptin = \
                "/usr/bin/molauto %s -r 2> /dev/null \
                | /usr/bin/molscript -r 2> /dev/null \
                | /usr/bin/render -size %s -jpeg > %s" % (pdb_in, size,
                                                          jpg_out)
            subprocess.check_call(molscriptin, shell=True)

    def generate_all_chimerax(self):
        output_pdbs = glob.glob('asmb.model.*.pdb')

        for pdb_in in output_pdbs:
            self.generate_chimerax(pdb_in, False)

    # Generate Chimera web data (chimerax) files
    def generate_chimerax(self, pdb_in, include_map_flag):
        (filepath, jobdir) = os.path.split(self.url)
        pdb_temp = "/" + pdb_in + "?"
        pdb_url = re.sub(r'\?', pdb_temp, jobdir)
        full_path = filepath + "/" + pdb_url

        (filename, extension) = os.path.splitext(pdb_in)
        chimerax_out = filename + ".chimerax"
        if include_map_flag:
            chimerax_out = filename + ".map.chimerax"
            map_temp = "/" + "input.mrc" + "?"
            map_url = re.sub(r'\?', map_temp, jobdir)
            map_path = filepath + "/" + map_url

        infile = open(chimerax_out, 'w')
        print("<?xml version=\"1.0\"?>", file=infile)
        print("<ChimeraPuppet type=\"std_webdata\">", file=infile)
        print("<web_files>", file=infile)
        print("   <file  name=\"%s\" format=\"text\" loc=\"%s\" />"
              % (pdb_in, full_path), file=infile)
        if include_map_flag:
            print("   <file  name=\"input.mrc\" format=\"mrc\" loc=\"%s\" />"
                  % map_path, file=infile)
        print("</web_files>", file=infile)
        print("""
<commands>
    <py_cmd>model = chimera.openModels.list()[0]</py_cmd>
    <mid_cmd>ribbon</mid_cmd>
    <mid_cmd>~disp</mid_cmd>
    <mid_cmd>modelcolor #fa8072 #0</mid_cmd>
    <mid_cmd>ribrepr smooth</mid_cmd>
""", file=infile)
        if include_map_flag:
            print("    <mid_cmd>vol all transparency 0.5</mid_cmd>",
                  file=infile)
            print("    <mid_cmd>vol all level 0.825</mid_cmd>", file=infile)
        print("</commands>", file=infile)
        print("</ChimeraPuppet>", file=infile)
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


def get_web_service(config_file):
    db = saliweb.backend.Database(Job)
    config = saliweb.backend.Config(config_file)
    return saliweb.backend.WebService(config, db)
