import saliweb.frontend
import os
import csv

def read_multifit_output_file(job):
    fname = job.get_path('multifit.output')
    if not os.path.exists(fname):
        return
    with open(fname) as fh:
        # Do our own parsing to get the fieldnames, since we need to strip
        # whitespace
        fn = fh.readline().rstrip('\r\n').split('|')
        r = csv.DictReader(fh, delimiter='|',
                           fieldnames=[x.strip() for x in fn])
        for sol in r:
            sol['ccc'] = 1. - float(sol['fitting score'])
            pdbnum = sol['solution filename'].split('.')[2]
            sol['chimera'] = 'asmb.model.%s.chimerax' % pdbnum
            sol['image'] = 'asmb.model.%s.jpg' % pdbnum
            yield sol


def show_results_page(job):
    fit_solutions = list(read_multifit_output_file(job))
    if fit_solutions:
        return saliweb.frontend.render_results_template(
            "results_ok.html", job=job, solutions=fit_solutions)
    else:
        return saliweb.frontend.render_results_template(
            "results_failed.html", job=job)
