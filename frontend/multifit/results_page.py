import saliweb.frontend
import os
import math
import re


class ValueWithError:
    def __init__(self, value, err):
        self.value = value
        self.err = err if err == 'nan' else float(err)

    def has_error(self):
        return self.err != 'nan' and self.err < self.value/10.


class Results:
    def __init__(self, job):
        self.job = job

    def file_exists(self, fname):
        return os.path.exists(self.job.get_path(fname))


class MergeStats:
    """Parse summary.txt file's merge section"""
    def __init__(self, fname):
        with open(fname) as fh:
            self.read_fh(fh)

    def read_fh(self, fh):
        numpoints_re = re.compile(r'Number of points: (\d+)')
        profilepoints_re = re.compile(
            r'(\d+) points from profile \d+ \((.+)\)')
        for line in fh:
            if line.startswith('Merge file'):
                break
        for line in fh:
            m = numpoints_re.search(line)
            if m:
                self.nmergepoints = int(m.group(1))
                break
        fh.readline()  # drop next line

        # get input filenames
        mergefiles = []
        mergefpoints = []
        for line in fh:
            if 'Gaussian Process parameters' in line:
                break
            m = profilepoints_re.search(line)
            if m:
                mergefpoints.append(int(m.group(1)))
                mergefiles.append(m.group(2))

        # get merge mean parameters
        self.mergemean = self._get_merge_param(fh)

        # get input mean parameters for each file
        self.inputmean = []
        for fname, fpoints in zip(mergefiles, mergefpoints):
            p = self._get_merge_param(fh)
            p['fname'], p['points'] = fname, fpoints
            p['pointpct'] = float(fpoints) / self.nmergepoints * 100.
            self.inputmean.append(p)

    def _get_merge_param(self, fh):
        param = {}

        mean_func_re = re.compile(r'mean function : (\w+)')
        for line in fh:
            m = mean_func_re.search(line)
            if m:
                param['mean'] = m.group(1)
                break

        valre = re.compile(r'(\w+) : (.+) \+- (.+)$')
        for line in fh:
            if 'Calculated Values' in line:
                break
            m = valre.search(line)
            key, val, err = m.group(1), float(m.group(2)), m.group(3)
            if key == 'sigma2':
                key = 'sigma'
                val = math.sqrt(val)
                if err != 'nan':
                    err = math.sqrt(float(err))
            param[key] = ValueWithError(val, err)
        return param


def show_results_page(job):
    if os.path.exists(job.get_path('summary.txt')):
        return saliweb.frontend.render_results_template(
            "results_ok.html", job=job, results=Results(job),
            merge_stats=MergeStats(job.get_path('summary.txt')))
    else:
        return saliweb.frontend.render_results_template(
            "results_failed.html", job=job)
