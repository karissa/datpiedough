from __future__ import absolute_import
from __future__ import unicode_literals

import json
import pickle
import unittest

from datpy import Dat, Dataset

try:
  import pandas as pd
except:
  pd = False

class DatTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    cls.dat = Dat()
    cls.dat.init()

  @classmethod
  def tearDownClass(cls):
    cls.dat.destroy()

class IsolatedTest(DatTest):

  def test_insert_with_dataset(self):
    dataset = Dataset(self.dat, 'contracts')
    version = dataset.import_file("examples/contracts.csv")
    self.assertEqual(len(version), 64)
    output = dataset.export()
    self.assertEqual(len(output), 770)

    status = self.dat.status()
    self.assertEqual(status['datasets'], 1)
    self.assertEqual(status['files'], 1)
    #self.assertEqual(status['rows'], 770)

    datasets = self.dat.datasets()
    self.assertEqual(len(datasets), 2)
    self.assertTrue('files' in datasets)
    self.assertTrue('contracts' in datasets)

class IOTests(DatTest):

  def test_insert_with_dataset(self):
    dataset = Dataset(self.dat, 'contracts')
    version = dataset.import_file("examples/contracts.csv")
    self.assertEqual(len(version), 64)
    output = dataset.export()
    self.assertEqual(len(output), 770)

  def test_insert_with_bad_path_fails(self):
    dataset = Dataset(self.dat, 'contracts2')
    with self.assertRaises(Exception):
        dataset.import_file("not-a-file.csv")

  def test_write_file(self):
    version = self.dat.write_file("examples/blob.txt")
    self.assertEqual(len(version), 64)
    output = self.dat.read("blob.txt")
    self.assertEqual(output, "hello world\n")

  def test_write_blob_from_python(self):
    version = self.dat.write("hello.txt", data="hello world")
    self.assertEqual(len(version), 64)
    self.assertEqual(self.dat.read("hello.txt"), "hello world")

  def test_write_dict_from_python(self):
    my_python_object = {
      "hello": "world",
      "goodbye": "mars"
    }
    binary_data = json.dumps(my_python_object)
    version = self.dat.write("helloworld_dict", data=binary_data)
    self.assertEqual(len(version), 64)

    out_data = self.dat.read("helloworld_dict")
    output = json.loads(out_data)
    self.assertEqual(type(output), dict)
    self.assertEqual(output["hello"], "world")

  def test_write_pickle_from_python(self):
    my_python_object = {
      "hello": "mars",
      "goodbye": "world"
    }
    data = pickle.dumps(my_python_object)
    version = self.dat.write("helloworld.pickle", data=data)
    self.assertEqual(len(version), 64)

    data = self.dat.read("helloworld.pickle")
    obj = pickle.loads(data)
    self.assertEqual(type(obj), dict)
    self.assertEqual(obj["hello"], "mars")


@unittest.skipIf(pd is False, "skipping pandas tests")
class TestPandas(DatTest):

  def test_pandas(self):
    # clean column, turn into float
    df = pd.read_csv('examples/contracts.csv')
    self.assertEquals(df.shape, (770, 10))

    df['amtSpent'] = df['amtSpent'].str.replace(r'[$,]', '')

    # insert data
    dataset = Dataset(self.dat, "pandas")
    version = dataset.import_dataframe(df)
    self.assertEqual(64, len(version))

    output = dataset.export()
    self.assertEqual(len(output), 770)

    df = dataset.export_dataframe()
    keys = list(dataset.keys())
    df['key'] = pd.Series(keys)

    # modify a column
    # create ranked column.
    df['amtSpentRank'] = df['amtSpent'].rank()
    self.assertEquals(df.shape, (770, 13))

    # okay, put it back in dat
    version = dataset.import_dataframe(df, key='key')
    self.assertEqual(len(version), 64)

    # and get it back out
    output = dataset.export()
    self.assertEqual(len(output), 770)
    df_with_rank = pd.DataFrame.from_dict(output)

    # get the new data in a data frame.
    # we should see the updated data and new column there.
    self.assertEquals(df_with_rank.shape, (770, 13))

    # do some type conversion
    # TODO: save dtypes and automagically parse them for the python user
    # if coming to/from pandas
    df_with_rank['amtSpentRank'] = df_with_rank['amtSpentRank'].astype('float')

    self.assertTrue(df_with_rank['amtSpentRank'].equals(df['amtSpentRank']))

if __name__ == '__main__':
  unittest.main()
