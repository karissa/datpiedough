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
    print("It looks like `dat` commandline is missing from PATH.\n",
          "Are you sure you installed it?\n"
          "Check http://dat-data.com for instructions")
  else:
   return p.returncode

class Dat:

  def __init__(self, location=None):
    if location:
      subprocess.call(["cd", self.location])
      self.location = location

    self.version = None

  def init(self):
    return subprocess.call(["dat init --no-prompt"], shell=True)

  def checkout(self, version):
    self.version = version
    return subprocess.call(["dat checkout " + version], shell=True)

  @returns_version
  def import_file(self, filename, **kwargs):
    p = process("dat import " + filename, kwargs)
    return p.communicate()

  @returns_version
  def import_dataframe(self, dataframe, **kwargs):
    ## TODO: make streaming by using a generator
    p = process("dat import -", kwargs)
    stdout, stderr = stream_in(p, dataframe.to_csv(), parse=True)
    return (stdout, stderr)

  @returns_version
  def write(self, data, name, **kwargs):
    p = process("dat write {0} -".format(name), kwargs)
    stdout, stderr = stream_in(p, data, parse=False)
    return (stdout, stderr)

  @returns_version
  def write_file(self, filename, **kwargs):
    p = process("dat write " + filename, kwargs)
    return p.communicate()

  def write_pickle(self, data, name, **kwargs):
    data = cPickle.dumps(data)
    return self.write(data, name, **kwargs)

  def read_pickle(self, name, **kwargs):
    data = self.read(name, **kwargs)
    return cPickle.loads(data)

  def read(self, name, **kwargs):
    return stream_out("dat read " + name, kwargs, parse=False)

  def export_dataframe(self, dataset, **kwargs):
    if not pd:
      raise Exception("Can't find pandas. Is it available on your path?")

    output = self.export(dataset, **kwargs)
    return pd.DataFrame.from_dict(output)

  def export(self, dataset, **kwargs):
    return stream_out("dat export -d " + dataset, kwargs)

  def clean(self):
    return subprocess.call(["rm -rf .dat"], shell=True)

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

def stream_in(p, data, parse=True):
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

def stream_out(cmd, opts=None, parse=True):
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
  p = process(cmd, opts)

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
