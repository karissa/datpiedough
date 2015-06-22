# DAT Python API

This is a client in python for [Dat](https://dat-data.com). There are functions to interact with the REST api as well as local hooks. It integrates easily with [pandas](http://pandas.pydata.org).

Hello, collaboration.

## What is Dat?

Dat is a open data project designed to make data more accessible:

* Track incremental changes made in datasets
* Designed to work with all data: big and small

Read the [docs](https://github.com/maxogden/dat) to learn more about Dat.

## Installation

  1. Install[dat](https://github.com/maxogden/dat)

  2. Install pip

  3. Obtain the Python DAT package

    `pip install datpy`

## Usage

This is a new library and it needs work! Please don't hesitate to send a pull request or to open an issue if you find something wrong or broken. It's probably because we messed up!

Here's a simple example of how to read a dat's data into a pandas object, and then update the dat accordingly after editing the values.

```python
from datpy import Dat
import pandas as pd

dat = Dat()

## initialize dat
dat.init(tempdir())

df = pd.read_csv('cities.csv')

## uses the unique column 'city_code' to identify and version rows over time
v1 = dat.import_dataframe(df, dataset="cities", key="city_code")

## get the data at a certain version
data = dat.export(dataset="cities", checkout=v1)
df_v1 = pd.DataFrame.from_dict(data)
```

[An ipython notebook example for dat](http://nbviewer.ipython.org/github/pkafei/Dat-Python/blob/master/examples/Using%20Python%20with%20Dat.ipynb) (outdated)

## datpy

```
pip install datpy
```

```python
import datpy
```

### clone

Clones the dat into a local directory on your filesystem.

`datpy.clone(URL, path, **kwargs*)`

Example:

```python
> import datpy
> mydat = datpy.clone('ssh://karissa@mydat.edu:/user/mydats/cities', "./cities")
```

### push

Push the dat somewhere. Defaults to the initial clone location.

```python
> mydat.push()
```

### pull

Replicate dat updates from your peer. Defaults to the initial clone location.

```python
> mydat.pull()
```

## Dat

`Dat` is a class that binds to a Dat on your hard drive. Datasets are loaded streaming from the filesystem into python's memory.

For very large datasets and for code in production, please refer to the [dat commandline documentation](https://github.com/maxogden/dat/blob/master/docs/cli-usage.md) for stable and memory-safe interaction.

```python
> import datpy
> mydat = datpy.Dat('./path/to/dat/repo')
> mydat.init()
```

For each command, a `dat` instance accepts any of the options supported by Dat's [commandline api](http://datproject.readthedocs.org/en/latest/cli-docs/)

For example, ```dataset='mydataset'`` expands to `dat export --dataset=mydataset`

### import_dataframe

Import rows from a pandas dataframe.

Returns the new version of the dat repository as a string.

```python
> df = pd.read_csv('examples/contracts.csv')
> mydat.import_dataframe(df, dataset="contracts", key='id')
'0eafefda2bcfee5'
```

### export_dataframe

Get data from the dat as a pandas dataframe.

```python
df = mydat.export_dataframe(dataset="contracts", checkout='0eafefda2bcfee5')
```

### write_pickle

Write any python data or object to dat as a cPickle, that is, as a compressed binary file on disk in the dat.

Returns the new version of the dat repository as a string.

```python
> my_python_object = {
  "hello": "mars",
  "goodbye": "world"
}
> name = "hello_world"
> mydat.write_pickle(my_python_object, name, dataset="blobs")
'ba13bead12a0db'
```

### read_pickle

Read a binary object from dat at a given version that has been stored as a python pickle.

```python
output = mydat.read_pickle(name, dataset="blobs", checkout='ba13bead12a0db')
```

#### import_file

Import rows from a tabular file into dat.

Returns the new version of the dat repository as a string.

```python
> mydat.import_file('tables/cities.csv', dataset='cities_data', key='cityId')
'abc2f3d234abc234ef1g13d'
```

#### export

Get the rows in the dat. This returns a list of dictionaries, where each dictionary is the json representation of that row.

```python
> mydat.export(checkout='abc2f3d234abc234ef1g13d')
[
  {'key': 'abc2f3d234abc234ef1g13d',
  'vote_share': 51.33,
  'state': 'CA',
  'republican': True},
  {'key': 'df1cdf3c23bc234ef1g13d',
  'vote_share': 49.53,
  'state': 'DE',
  'republican': False},
  ...
]
```

# Developers

This is a new library and it needs work! Please don't hesitate to send a pull request.

## Contributing

First, create a fork, then install the requirements. Make your change and open a pull request!

```bash
$ git clone http://github.com/<your-fork>/Dat-Python
$ pip install -r requirements.txt
$ git commit -am "BUG: there was a bug that had this problem"
$ git push origin master
 ... open pull request!
```

## Testing

Install `nosetests` for the best testing environment. If you don't have `pandas` installed, it will skip the pandas tests.

```bash
nosetests
```

To run just one test

```bash
nosetests test.py:SimpleTest.test_rows
```

To run the entire suite without `nosetests`:

```bash
python test.py
```


# BSD Licensed

Copyright (c) 2014 Karissa McKelvey and contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
