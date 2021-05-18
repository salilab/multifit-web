from flask import request
import saliweb.frontend
from saliweb.frontend import InputValidationError


def handle_new_job():
    job_name = request.form.get('job_name')
    email = request.form.get('email')
    input_map = request.files.get('map')
    resolution = request.form.get('resolution', type=float)
    spacing = request.form.get('spacing', type=float)
    threshold = request.form.get('threshold', type=float)
    x_origin = request.form.get('x_origin', type=float)
    y_origin = request.form.get('y_origin', type=float)
    z_origin = request.form.get('z_origin', type=float)
    input_symm_pdb = request.files.get('symm_pdb')
    cn_symmetry = request.form.get('cn_symmetry', type=int)

    # Validate input
    saliweb.frontend.check_email(email, required=False)
    if resolution is None:
        raise InputValidationError(
            "Map resolution input is missing or invalid.")
    if spacing is None:
        raise InputValidationError(
            "Vector spacing input is missing or invalid.")
    if cn_symmetry is None or cn_symmetry < 3:
        raise InputValidationError(
            "Cn symmetry should be an integer, of 3 or more.")
    if threshold is None:
        raise InputValidationError(
            "Contour level input is missing or invalid.")
    if x_origin is None or y_origin is None or z_origin is None:
        raise InputValidationError("Origin input is invalid.")
    if not input_map:
        raise InputValidationError("Please upload input density map.")
    if not input_symm_pdb:
        raise InputValidationError(
            "Please select upload subunit PDB coordinate file.")

    job = saliweb.frontend.IncomingJob(job_name)
    input_map.save(job.get_path('input.mrc'))
    output_file_name = job.get_path('input.pdb')
    input_symm_pdb.save(output_file_name)
    if not has_atoms(output_file_name):
        raise InputValidationError("PDB file contains no ATOM records!")

    # write parameters
    with open(job.get_path('param.txt'), 'w') as datafile:
        print("%f\n%f\n%f\n%f\n%f\n%f\n%d\n"
              % (resolution, spacing, threshold, x_origin, y_origin,
                 z_origin, cn_symmetry), file=datafile)

    job.submit(email)
    return saliweb.frontend.render_submit_template('submit.html', email=email,
                                                   job=job)


def has_atoms(fname):
    """Return True iff fname has at least one ATOM record"""
    with open(fname) as fh:
        for line in fh:
            if line.startswith('ATOM  '):
                return True
