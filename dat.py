import subprocess
import cPickle

try:
  import ujson as json
except:
  import json

try:
  import pandas as pd
except:
  pd = False

def returns_version(func):
  def inner(*args, **kwargs):
    stdout, stderr = func(*args, **kwargs)
    log = json.loads(stdout)
    self = args[0]
    self.version = log["version"]
    return self.version

  return inner

def clone(URL, path, **kwargs):
  """
  Parameters
  """
  p = process("dat clone {0} {1}".format(URL, path), kwargs)
  stdout, stderr = p.communicate()
  if p.returncode == 0:
    return Dat(path)
  elif p.returncode == 127:
    raise Exception("It looks like `dat` commandline is missing from PATH.\n",
                    "Are you sure you installed it?\n"
                    "Check http://dat-data.com for instructions")
  else:
   return p.returncode

class Dat:

  def __init__(self, path=None):
    if path:
      subprocess.call(["cd", self.path])
      self.path = path

    self.version = None

  def init(self):
    return subprocess.call(["dat init --no-prompt"], shell=True)

  def checkout(self, version):
    self.version = version
    return subprocess.call(["dat checkout " + version], shell=True)

  def push(self, URL, **kwargs):
    return stream_out("dat push " + URL, kwargs, parse=False)

  def pull(self, URL, **kwargs):
    return stream_out("dat pull " + URL, kwargs, parse=False)

  def clean(self):
    return subprocess.call(["rm -rf .dat"], shell=True)

class Dataset:

  def __init__(self, dat, dataset, key=None):
    self.dat = dat
    self.dataset = dataset
    self.key = key

  @returns_version
  def import_file(self, filename, **kwargs):
    p = self.process("dat import " + filename, kwargs)
    return p.communicate()

  @returns_version
  def import_dataframe(self, dataframe, **kwargs):
    ## TODO: make streaming by using a generator
    if not kwargs['key']:
      kwargs['key'] = self.key

    p = self.process("dat import -", kwargs)
    stdout, stderr = stream_in(p, dataframe.to_csv())
    return (stdout, stderr)

  @returns_version
  def write(self, filename, data=None, **kwargs):
    if not data:
      self.write_file(filename, **kwargs)

    p = self.process("dat write {0} -".format(filename), kwargs)
    stdout, stderr = stream_in(p, data)
    return (stdout, stderr)

  @returns_version
  def write_file(self, filename, **kwargs):
    p = self.process("dat write " + filename, kwargs)
    return p.communicate()

  def read(self, key, **kwargs):
    p = self.process("dat read " + key, kwargs)
    return stream_out(p, parse=False)

  def export_dataframe(self, **kwargs):
    if not pd:
      raise Exception("Can't find pandas. Is it available on your path?")

    output = self.export(**kwargs)
    frame = pd.DataFrame.from_dict(output['value'])
    frame[self.key] = output[self.key]
    return frame

  def export(self, **kwargs):
    p = self.process("dat export", kwargs)
    return stream_out(p)

  def process(self, cmd, opts):
    opts['dataset'] = self.dataset
    if self.key:
      opts['key'] = self.key

    return process(cmd, opts)

def process(cmd, opts):
  """
  Creates a process.
  Adds options (provided as keyword args) to the given cmd.

  Parameters
  ----------
  cmd: str
    the command to add options
  opts: dict
    the options to add
  """
  if opts is None:
    opts = {}

  cmd += ' --json '

  for key, val in opts.iteritems():
    if (len(key) == 1):
      cmd += " -{0} {1}".format(key, val)
    else:
      cmd += " --{0}={1}".format(key, val)

  return subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

def stream_in(p, data):
  """
  Streams to dat from the given command into python

  Parameters
  ----------
  cmd: str
    the command to execute
  parse: boolean
    TODO: if true, will try to parse the output from python generator or list

  """
  out = p.communicate(input=data)
  if p.returncode == 1:
    raise Exception(out[1])
  else:
    return out

def stream_out(p, parse=True):
  """
  Streams the stdout from the given command into python

  Parameters
  ----------
  cmd: str
    the command to execute
  parse: boolean
    if true, will try to parse the output from json objects to
    python lists/dictionaries
  """
  if parse:
    res = []
    for line in iter(p.stdout.readline, ''):
      parsed = json.loads(line.rstrip())
      res.append(parsed)
  else:
    res = ''
    for line in iter(p.stdout.readline, ''):
      res += line

  subprocess.Popen.terminate(p)
  return res
