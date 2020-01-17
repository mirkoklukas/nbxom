#AUTOGENERATED! DO NOT EDIT! File to edit: dev/om.ipynb (unless otherwise specified).

__all__ = ['extract_tag', 'contains_tag', 'is_nbx', 'is_nbx_cell', 'is_magic_or_shell', 'strip', 'parse_xarg',
           'get_imports_from_src', 'Import', 'create_import_statement', 'extract_imports_from', 'Bunch', 'load_nb',
           'parse_src', 'parse_nbx_cell', 'concat', 'unzip', 'negate', 'is_constarg', 'get_item', 'get_items',
           'not_constarg', 'parse_nb', 'get_arrays', 'init_job', 'cont_job', 'chain_jobs', 'check_parsed_nb',
           'NbxBundle', 'BUNDLE_SUMMARY']

#Cell
#default_exp om
import re
_re_tag = re.compile(r"^\s*#([a-zA-Z_]+).*$")

#Cell
def extract_tag(line):
    """Returns the name of a tag (#name), if it
    occurs at the beginning of the line, or None."""
    m = _re_tag.match(line)
    if m is not None: return m.group(1)
    else: return None

#Cell
def contains_tag(name):
    return lambda line: extract_tag(line) == name

is_nbx = contains_tag("nbx")

#Cell
def is_nbx_cell(cell):
    if cell['cell_type'] != 'code': return False
    if not cell['source']: return False
    line0 = cell['source'][0]
    return is_nbx(line0)

#Cell
_re_magic =  re.compile(r"^\s*%{1,2}|^\s*!")

#Cell
def is_magic_or_shell(line):
    m = _re_magic.match(line)
    return m is not None

#Cell
_re_xarg = re.compile(r"""
# parses the line below an `xarg` tag:
^
([^=]+)
=
([^;]+)
;?
(.*)
$""", re.VERBOSE)

#Cell
def strip(s):
    return s.strip()

def parse_xarg(line):
    m = _re_xarg.match(line)
    name, val, sweep = map(strip, m.groups())
    return name, val, sweep

#Cell
import ast
from collections import namedtuple

Import = namedtuple("Import", ["module", "name", "alias"])

def get_imports_from_src(src):
    """Taken from:
        https://stackoverflow.com/questions/9008451/python-easy-way-to-read-all-import-statements-from-py-module
    """
    root = ast.parse(src)
    start = None
    end = None
    occ = []
    imp = []
    stm = []
    for node in ast.iter_child_nodes(root):
        occ.append((node.lineno))

        if isinstance(node, ast.Import):
            imp.append(True)
            module = []
        elif isinstance(node, ast.ImportFrom):
            imp.append(True)
            module = node.module.split('.')
        else:
            imp.append(False)
            continue

        for n in node.names:
            stm.append(Import(".".join(module), n.name, n.asname))

    print(occ)

    ign = []
    lines = src.split("\n")
    occ.append(len(lines))
    for i in range(len(occ)-1):
        if imp[i] == True:
            ign.extend(range(occ[i]-1,occ[i+1]-1))


    return stm, ign

#Cell
def create_import_statement(module, name, alias):
    if module == '':
        return f"import {name}" + ("" if alias == None else f" as {alias}")
    else:
        return f"from {module} import {name}" + ("" if alias == None else f" as {alias}")

#Cell
def extract_imports_from(src):
    imps, ign = get_imports_from_src(src)
    return [create_import_statement(*im) for im in imps], ign

#Cell
import json
from argparse import Namespace

class Bunch(object):
    def __init__(self, adict={}):
        self.__dict__.update(adict)

    def __repr__(self):
        return str(self.__dict__.keys())

def load_nb(fname):
    nbdict = json.load(open(fname,'r',encoding="utf-8"))
    return Bunch(nbdict)

#Cell
def parse_src(a, src):
    if len(src) == 0: return a, []

    tag = extract_tag(src[0])
    if tag is None:
        if not is_magic_or_shell(src[0]):
            a['xbody'].append(src[0])
        rest = src[1:]

    elif tag == 'nbx':
        a['xbody'].append(src[0])
        rest = src[1:]

    elif tag == 'xarg':
        a['xarg'].append(src[1])
        rest = src[2:]

    else:
        rest = src[1:]

    return parse_src(a, rest)


def parse_nbx_cell(cell):
    a = {'xbody': [], 'xarg': [] }
    a, _ = parse_src(a, cell['source'])
    return a['xarg'], a['xbody']

#Cell
from functools import reduce

def concat(list1, list2):
    return list1 + list2

def unzip(zipped):
    return zip(*zipped)

def negate(func):
    return lambda x: not func(x)

def is_constarg(a):
    return len(a[2]) == 0

not_constarg = negate(is_constarg)

def get_item(i):
    return lambda x: x[i]

def get_items(*I):
    return lambda x: tuple([x[i] for i in I])

#Cell
def parse_nb(nb):
    nbx_cells = filter(is_nbx_cell, nb.cells)

    xargs = []
    xbody = []
    for cell in nbx_cells:
        xa, xb = parse_nbx_cell(cell)
        xargs += [parse_xarg(line) for line in xa]
        xbody += xb

    pnb = Bunch()
    pnb.func_body = xbody
    pnb.args = list(map(get_items(0,1), xargs))
    pnb.const_args = list(map(get_items(0,1), filter(is_constarg, xargs)))
    pnb.sweep_args = list(map(get_items(0,2), filter(not_constarg, xargs)))

    return pnb


#Cell
def get_arrays(num, m=1000):
    if num < m: return [[1,num]]

    arrays = []
    for i in range(num//m): arrays.append([i*m+1, (i+1)*m])
    last = arrays[-1][1]
    if last < num: arrays.append([last+1, num])

    return arrays

#Cell
def init_job(start, end, step):
    return f"job_0=`sbatch --array={start}-{end}%{step} job.sh | awk '{{ print $4 }}'`"
def cont_job(j, start, end, step):
    return f"job_{j}=`sbatch --array={start}-{end}%{step} --dependency=afterok:$job_{j-1} job.sh | awk '{{ print $4 }}'`"

def chain_jobs(arrays, step):
    s = ""
    for i, arr in enumerate(arrays):
        if i ==0: s += init_job(arr[0], arr[1], step)
        else: s += cont_job(i, arr[0], arr[1], step)
        s += "\n"

    return s

#Cell
from pathlib import Path
import pkg_resources
import importlib
from .templ import *
import os

def check_parsed_nb(pnb):
    keys = list(map(get_item(0), pnb.args))
    if "task_id" not in keys: raise KeyError("You didn't specify `task_id`!!")
    if "results_dir" not in keys: raise KeyError("You didn't specify `results_dir`!!")

class NbxBundle():
    def __init__(self,
                 nbname,
                 mail_user,
                 name=None,
                 linting=True,
                 time=[1,0],
                 ntasks=10,
                 step=5,
                 simg="pytorch.simg",
                 max_arr=1000,
                 mem_per_cpu=2000):

        if name is None:
            name = Path(nbname).stem

        self.max_arr = max_arr
        self.nbname = nbname
        self.name = name
        self.path = Path(f"{name}_nbx")

        nb = load_nb(nbname)
        nb = parse_nb(nb)
        self.nb = nb

        check_parsed_nb(nb)

        self.create_folders()
        self.create_script("experiment.tpl", "experiment.py", vars(nb));


        p = ".".join((self.path/'experiment').parts)
        exp =  importlib.import_module(p)
        len(exp.sweep_params)
        self.num_configs = len(exp.sweep_params)


        self.create_run_script(len(exp.sweep_params), step, max_arr)

        self.create_script("wrapper.tpl", "wrapper.py", {
            'experiment_module': "experiment"});
        self.create_script("job.tpl", "job.sh", {
            'job_name': name,
            'nbx_folder': os.environ['omx'],
            'script_to_run': "wrapper.py",
            'results_dir': "./results",
            'hours': time[0],
            'mins': time[1],
            'ntasks': ntasks,
            'script': 'wrapper.py',
            'simg': Path(os.environ['omsimg'])/simg,
            'mail_user': mail_user,
            'mem_per_cpu': mem_per_cpu
        });

        print(self)
        if linting: self.check_scripts()

    def create_run_script(self, num, step, max_arr):
        path = self.path/'run.sh'
        with open(path, "w") as f:
            f.write("#!/bin/sh\n\n")
            f.write(chain_jobs(get_arrays(num, max_arr), step))

    def create_script(self, tname, fname, vars):
        tpath = Path(pkg_resources.resource_filename(
                     __name__, f"/templates/{tname}"))

        create_file_from_template(tpath,
            self.path/fname, vars)


    def create_folders(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            os.makedirs(self.path/'io')

        if os.path.exists('./src'):
            if not os.path.exists(self.path/'src'):
                os.makedirs(self.path/'src')
            os.system(f"cp -r src/* {self.path/'src'}")

        open(self.path/'__init__.py', 'a').close()


    def run_experiment(self):
        self.run()
        print("check status with `ssh $om squeue -u $omid` or `bundle.status()`")
        print("pull results with `bundle.pull_results()`")

    def __str__(self):
        return render_template_from_string(BUNDLE_SUMMARY,
                                           vars(self))

    def _run_command(self, cmd):
        stream = os.popen(cmd)
        output = stream.read()
        return output.strip()

    def push(self):
        cmd = f"scp -r {self.path} $om:$omx"
        output = self._run_command(cmd)
        if len(output) > 0:
            print(output)

    def run(self):
        cmd = f"ssh $om sbatch -D $omx/{self.path} $omx/{self.path}/run.sh"
        print(self._run_command(cmd))

    def status(self):
        cmd = f"ssh $om squeue -u $omid"
        print(self._run_command(cmd))

    def pull_results(self):
        cmd = f"scp -r $om:$omx/{self.path}/results ./{self.path}"
        output = self._run_command(cmd)
        if len(output) > 0:
            print(output)

        print(f"copied to `{self.path}/results/")

    def check_scripts(self):
        output = self._run_command(f"pylint -E {self.path/'wrapper.py'}")
        if len(output) > 0:
            print(output)
            raise "Check wrapper script"

        output = self._run_command(f"pylint -E {self.path/'experiment.py'}")
        if len(output) > 0:
            print(output)
            raise "Check experiment script"

        print("(pylinting went ok)")


BUNDLE_SUMMARY = """
** nbx bundle created **
Path:
    {{path}}

Source nb:
    {{nbname}}

Parameters (#configs {{num_configs}}):
    {% for k,v in nb.sweep_args %}* {{k}} = {{v}}{% if not loop.last %}
    {% endif %}{% endfor %}
    {% for k,v in nb.const_args %}  {{k}} = {{v}}{% if not loop.last %}
    {% endif %}{% endfor %}

Instructions:
    Copy to remote, run the bash script, and pull the results
    - `bundle.push()` or `scp -r {{path}} $om:$omx`
    - `bundle.run()` or `ssh $om sbatch -D $omx/{{path}} $omx/{{path}}/run.sh`
    - `bundle.pull_results()` or `scp -r $om:$omx/{{path}}/results ./results`
"""
