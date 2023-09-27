# -*- coding: utf-8 -*-
"""
Unit tests for the binda module

Created on Wed Sep 20 15:48:53 2023

@author: Jamie Cash
"""

import binda as bd
import pandas as pd
import struct
import unittest


class TestVariable(unittest.TestCase):

    def test_next_offset(self):
      # Create a 4 byte variable starting at offset 12. Test that next offset
      # returns 16.
      var = bd.Variable('name', 4, int, 12)
      
      self.assertEqual(var.next_offset, 16)
      

class TestStructure(unittest.TestCase):
  
  def test_offset_autopopulate(self):
    # Test that structures auto populate variables offset correctly.
    
    # Define the variables. Don't set some of the offsets. These will be auto 
    # populated by the Structure
    variables = [
      bd.Variable('name', 20, str),
      bd.Variable('address', 100, str),
      # Set offset on this one only
      bd.Variable('age', 2, int, 120, byteorder=bd.ByteOrder.BIG),
      bd.Variable('balance', 2, float, byteorder=bd.ByteOrder.LITTLE, 
                  signed=True)
    ]

    # Create the structure
    bd.Structure(0, variables)

    # Test that the offsets have been auto populated
    self.assertEqual(variables[0].offset, 0)
    self.assertEqual(variables[1].offset, 20)
    self.assertEqual(variables[2].offset, 120)
    self.assertEqual(variables[3].offset, 122)
    
  def test_len(self):
    # Test that the length of the structure is correct
    
    # Define a structure of 123 bytes consisting of 3 variables.
    variables = [
      bd.Variable('name', 20, str),
      bd.Variable('address', 100, str),
      bd.Variable('age', 1, int, byteorder=bd.ByteOrder.BIG),
      bd.Variable('balance', 2, float, byteorder=bd.ByteOrder.LITTLE, 
                  signed=True)
    ]
    
    # Create the structure
    structure = bd.Structure(0, variables)
   
    # Test its length
    self.assertEqual(len(structure), 123)
    
    
class TestDataHandler(unittest.TestCase):
  
  @property
  def data(self):
    """
    Some binary for the unit tests.
    
    * The first 9 bytes contain 'BLOCKDATA',
    * The next 51 bytes contains a repeating structure of 3 record, each 
      consisting of a 1 byte ID, a 15 bytes NAME and a 1 byte ACTIVE flag,
    * The next 18 bytes contains a non repeating structure consisting of a 15 
        bytes AUTHOR, a 2 bytes ID and a 2 bytes bigendian signed int POINTS.

    Returns:
      (bytes): The created data.
    """
    testdata = b"BLOCKDATA"
    testdata += int(100).to_bytes(1, 'little')
    testdata += b"Jamie Cash     "
    testdata += bool(True).to_bytes(1, 'little')
    testdata += int(101).to_bytes(1, 'little')
    testdata += b"Bobby Smith    "
    testdata += bool(False).to_bytes(1, 'little')
    testdata += int(102).to_bytes(1, 'little')
    testdata += b"Mr Bean        "
    testdata += bool(True).to_bytes(1, 'little')
    testdata += b"Mr Author      "
    testdata += int(10).to_bytes(2, 'little')
    testdata += int(-20).to_bytes(2, byteorder='big', signed=True)
    testdata += struct.pack('<f', float(123.5))
    
    return testdata
  
  @property
  def structures(self):
    """
    The structures for the unit tests.
    """

    # Define the structure of the non repeating data
    start = 60
    variables = []
    variables.append(bd.Variable('AUTHOR', 15, str))
    variables.append(bd.Variable('ID', 2, int))
    variables.append(bd.Variable('POINTS', 2, int, byteorder=bd.ByteOrder.BIG, 
                                 signed=True))
    variables.append(bd.Variable('BALANCE', 4, float))
    structure = bd.Structure(start=start, variables=variables)

    # Define the structure of the repeating data
    start = 9
    variables = []
    variables.append(bd.Variable('ID', 1, int))
    variables.append(bd.Variable('NAME', 15, str))
    variables.append(bd.Variable('ACTIVE', 1, bool))
    table = bd.Structure(start=start, variables=variables, rows=3)

    # Define the structures and return
    structures={'author': structure, 'people': table}
    
    return structures
  
  def test_read_variable(self):
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)
    
    # Test that the string AUTHOR at offset 60 can be read. 
    data = handler.read_variable(bd.Variable('AUTHOR', 15, str, 60))
    self.assertEqual(type(data), str)
    self.assertEqual(data, 'Mr Author      ')
    
    # Test that the little endian int ID at offset 75 can be read. 
    data = handler.read_variable(bd.Variable('ID', 2, int, 75))
    self.assertEqual(type(data), int)
    self.assertEqual(data, 10)

    # Test that the big endian signed int POINTS at offset 77 can be read. 
    data = handler.read_variable(bd.Variable('POINTS', 2, int, 77, 
                                             bd.ByteOrder.BIG, signed=True))
    self.assertEqual(type(data), int)
    self.assertEqual(data, -20)
    
    # Test that the float BALANCE at offset 79 can be read. 
    data = handler.read_variable(bd.Variable('BALANCE', 4, float, 79))
    self.assertEqual(type(data), float)
    self.assertEqual(data, 123.5)
    
  def test_write_variable(self):
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)
    
    # Test that the string AUTHOR at offset 60 can be changed. 
    var = bd.Variable('AUTHOR', 15, str, 60)
    data = handler.read_variable(var)
    self.assertEqual(data, 'Mr Author      ')
    handler.write_variable('Sir Author     ', var)
    data = handler.read_variable(var)
    self.assertEqual(data, 'Sir Author     ')
    
    # Test that the little endian int ID at offset 75 can be changed. 
    var = bd.Variable('ID', 2, int, 75)
    data = handler.read_variable(var)
    self.assertEqual(data, 10)
    handler.write_variable(20, var)
    data = handler.read_variable(var)
    self.assertEqual(data, 20)

    # Test that the big endian signed int POINTS at offset 77 can be read. 
    var = bd.Variable('POINTS', 2, int, 77, bd.ByteOrder.BIG, signed=True)
    data = handler.read_variable(var)
    self.assertEqual(data, -20)
    handler.write_variable(-40, var)
    data = handler.read_variable(var)
    self.assertEqual(data, -40)
    
    # Test that the float BALANCE at offset 79 can be read. 
    var = bd.Variable('BALANCE', 4, float, 79)
    data = handler.read_variable(var)
    self.assertEqual(data, 123.5)  
    handler.write_variable(123.75, var)
    data = handler.read_variable(var)
    self.assertEqual(data, 123.75)
    
  def test_read_single_structure(self):
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)
    
    # Read the authors structure
    author = handler.read_structure('author')

    # Test that it is correct
    self.assertEqual(author.iloc[0].all(), 
                     pd.Series({'AUTHOR': 'Mr Author      ', 
                                'ID': 10,
                                'POINTS': -20, 
                                'BALANCE': 123.5}).all())
  
  def test_read_repeating_structure(self):  
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)
    
    # Read the people repeating structure
    people = handler.read_structure('people')

    # Check that it is correct
    self.assertEqual(people.iloc[0].all(), 
                     pd.Series({'ID': 100, 
                                'NAME': 'Jamie Cash     ',
                                'ACTIVE': True}).all())
    self.assertEqual(people.iloc[1].all(),
                     pd.Series({'ID': 101, 
                                'NAME': 'Bobby Smith    ',
                                'ACTIVE': False}).all())
    self.assertEqual(people.iloc[2].all(),
                     pd.Series({'ID': 102, 
                                'NAME': 'Mr Bean        ',
                                'ACTIVE': True}).all())
    
  def test_write_single_structure(self):
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)
    
    # Read the authors structure.
    author = handler.read_structure('author')
    
    # Change the authors name to Sir Author, his ID to 11, his points to 100 
    # and his balance to 12345.75 and write it back.
    author.loc[0, 'ID'] = 11
    author.loc[0, 'AUTHOR'] = 'Sir Author    '
    author.loc[0, 'POINTS'] = 100
    author.loc[0, 'BALANCE'] = 12345.75
    handler.write_structure('author', author)
    
    # Read it again
    author = handler.read_structure('author')
    
    # Test that it is correct
    self.assertEqual(author.iloc[0].all(), 
                     pd.Series({'AUTHOR': 'Sir Author    ', 
                                'ID': 11,
                                'POINTS': 100, 
                                'BALANCE': 12345.75}).all())
    
  def test_write_repeating_structure(self):
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)
    
    # Read the people repeating structure.
    people = handler.read_structure('people')
    
    # Change Bobby Smiths name to Bobby Smythe, his ID to 200 and is active 
    # status to True
    people.loc[people['ID'] == 101, 'ID'] = 200
    people.loc[people['ID'] == 200, 'NAME'] = 'Bobby Smythe   '
    people.loc[people['ID'] == 200, 'ACTIVE'] = True
    handler.write_structure('people', people)
    
    
    # Read it again
    people = handler.read_structure('people')
    
    # Test that it is correct
    self.assertEqual(people.iloc[1].all(),
                     pd.Series({'ID': 200, 
                                'NAM': 'Bobby Smythe   ',
                                'ACTIVE': True}).all())
    
  def test_read_hex(self):
    # Create the DataHandler 
    handler = bd.DataHandler(self.data, self.structures)

    # The 10 bytes starting at position 5 should have a hex string of 
    # '44|41|54|41|64|4a|61|6d|69|65' when seperated by |
    assert handler.read_hex(5,10, '|') == '44|41|54|41|64|4a|61|6d|69|65'

    # Test the defaults. The length of the string shold be length of data * 
    # 3 - 1 as there are 3 characters for each byte including the seperator,
    # except for the last byte where there isn't a seperator.
    assert len(handler.read_hex()) == len(self.data) * 3 -1


if __name__ == '__main__':
    unittest.main()