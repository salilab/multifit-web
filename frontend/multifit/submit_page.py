from flask import request
import saliweb.frontend
from saliweb.frontend import InputValidationError
from werkzeug.utils import secure_filename
import re
import os


def handle_new_job():
    email = request.form.get('jobemail')

    # Validate input
    saliweb.frontend.check_email(email, required=False)
    records = request.form.get('recordings', type=int)
    if records is None or records < 2:
        raise InputValidationError(
                "The number of times each profile has been recorded must "
                "be at least 2!")

    job = saliweb.frontend.IncomingJob()

    # write parameters
    with open(job.get_path('input.txt'), 'w') as datafile:
        handle_profiles(request.files.getlist("uploaded_file"), records,
                        datafile, job)
        add_advanced_options(datafile, job)

    job.submit(email)
    return saliweb.frontend.redirect_to_results_page(job)


def add_advanced_options(datafile, job):

    def add_bool_option(reqname, outflag):
        if request.form.get(reqname):
            print(outflag, file=datafile)

    def add_not_bool_option(reqname, outflag):
        if not request.form.get(reqname):
            print(outflag, file=datafile)

    def add_float_option(reqname, outflag, error_msg=None):
        val = request.form.get(reqname, type=float)
        if val is not None:
            print("%s=%f" % (outflag, val), file=datafile)
        elif error_msg:
            raise InputValidationError(error_msg)

    def add_choice_option(reqname, outflag, choices):
        choice = request.form.get(reqname)
        if choice in choices:
            print("%s=%s" % (outflag, choice), file=datafile)
        else:
            raise InputValidationError(
                "%s must be one of %s" % (reqname, choices))

    add_bool_option('gen_auto', '--auto')
    add_bool_option('gen_header', "--header")
    add_bool_option('gen_noisy', "--remove_noisy")
    add_bool_option('gen_redundant', "--remove_redundant")
    add_bool_option('gen_input', "--allfiles")

    mult = 1
    if request.form.get('gen_unit') == 'Nanometer':
        mult = 10
        with open(job.get_path('is_nm'), 'w') as fh:
            fh.write('nm')

    add_choice_option('gen_output',  "--outlevel",
                      ['sparse', 'normal', 'full'])
    add_choice_option('gen_stop',  "--stop",
                      ['cleanup', 'fitting', 'rescaling', 'classification',
                       'merging'])

    # cleanup
    add_float_option('clean_alpha', '--aalpha')

    # fitting
    add_choice_option('fit_param',  "--bmean",
                      ['Flat', 'Simple', 'Generalized', 'Full'])
    add_not_bool_option('fit_comp', '--bnocomp')
    add_bool_option('fit_bars', '--berror')

    # rescaling
    add_choice_option('res_model',  "--cmodel",
                      ['normal', 'normal-offset', 'lognormal'])

    # classification
    add_float_option('class_alpha', '--dalpha',
                     "Advanced: classification: alpha is invalid number")

    # merging
    add_choice_option('merge_param',  "--emean",
                      ['Flat', 'Simple', 'Generalized', 'Full'])
    add_not_bool_option('merge_comp', '--enocomp')
    add_bool_option('merge_bars', '--eerror')
    add_bool_option("merge_noextrapol", "--enoextrapolate")

    # expert options
    # general
    if request.form.get("gen_npoints_input"):
        print("--npoints=-1", file=datafile)
    else:
        qnum = request.form.get("gen_npoints_val", type=int)
        if qnum is None or qnum <= 0:
            raise InputValidationError(
                "Expert: general: q values not a positive number")
        print("--npoints=%d" % qnum, file=datafile)
    add_bool_option("gen_postpone", "--postpone_cleanup")

    # cleanup
    qcut = request.form.get("clean_cut", type=float)
    if qcut is None or qcut <= 0:
        raise InputValidationError(
            "Expert: cleanup: q cutoff is invalid positive float")
    print("--acutoff=%f" % qcut * mult, file=datafile)

    # fitting
    add_bool_option("fit_avg", "--baverage")

    # rescaling
    add_choice_option('res_ref',  "--creference", ['first', 'last'])
    ngamma = request.form.get("res_npoints", type=int)
    if ngamma is None or ngamma <= 0:
        raise InputValidationError(
            "Expert: rescaling: number of gamma points must be >0")
    print("--cnpoints=%d" % ngamma, file=datafile)

    # merging
    add_bool_option("merge_avg", "--eaverage")
    nextrapol = request.form.get("merge_extrapol", type=int)
    if nextrapol is None or nextrapol < 0:
        raise InputValidationError(
            "Expert: merging: percentage must be positive integer")
    print("--eextrapolate=%d" % nextrapol, file=datafile)


def handle_profiles(fhs, records, datafile, job):
    """Save uploaded profiles into the job directory."""
    if not fhs:
        raise InputValidationError("Please input at least one file!")
    for fh in fhs:
        fname = secure_filename(os.path.basename(fh.filename))
        # Make sure it doesn't contain = either since that will confuse
        # parsing of the datafile
        fname = fname.replace('=', '')
        if len(fname) > 40:
            raise InputValidationError(
                "Please limit the file name length to a maximum of "
                "40 characters")
        if re.search('(zip|tar|gz|bz2|rar)$', fname):
            raise InputValidationError(
                "Please provide plain text files with three columns (q,I,err)")

        fh.save(job.get_path(fname))
        print("%s=%d" % (fname, records), file=datafile)
