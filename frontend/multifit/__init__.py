from flask import render_template, request, send_from_directory, abort
import saliweb.frontend
from saliweb.frontend import get_completed_job, Parameter, FileParameter
from . import submit_page, results_page
import re


parameters = [Parameter("job_name", "Job name", optional=True),
              FileParameter("map", "Density map"),
              Parameter("resolution", "Resolution for the density map"),
              Parameter("spacing", "Spacing for the density map"),
              Parameter("threshold", "Threshold for the density map"),
              Parameter("x_origin", "X origin for the density map"),
              Parameter("y_origin", "Y origin for the density map"),
              Parameter("z_origin", "Z origin for the density map"),
              FileParameter("symm_pdb", "Input PDB for symmetry case"),
              Parameter("cn_symmetry", "Number of Cn symmetry")]
app = saliweb.frontend.make_application(__name__, parameters)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/job', methods=['GET', 'POST'])
def job():
    if request.method == 'GET':
        return saliweb.frontend.render_queue_page()
    else:
        return submit_page.handle_new_job()


@app.route('/results.cgi/<name>')  # compatibility with old perl-CGI scripts
@app.route('/job/<name>')
def results(name):
    job = get_completed_job(name, request.args.get('passwd'))
    return results_page.show_results_page(job)


def get_mime_type(fp):
    if fp.endswith('chimerax'):
        return 'application/x-chimerax'
    elif fp.endswith('pdb'):
        return 'chemical/x-pdb'
    elif fp.endswith('output'):
        return 'text/plain'


allowed_re = re.compile(r'asmb\.model\..*(jpg|pdb|chimerax)')


def allowed_file(fp):
    return (fp in ('multifit.output', 'multifit.log',  'scores.output',
                   'dockref.output', 'input.mrc', 'asmb_models.tar.gz')
            or allowed_re.match(fp))


@app.route('/job/<name>/<path:fp>')
def results_file(name, fp):
    job = get_completed_job(name, request.args.get('passwd'))
    if allowed_file(fp):
        return send_from_directory(job.directory, fp,
                                   mimetype=get_mime_type(fp))
    else:
        abort(404)
