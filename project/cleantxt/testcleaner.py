# -*- coding: utf-8 -*-
import unittest
import os

import cleaner
basepath = os.path.dirname(__file__)

def openrel(file_name):
  filepath = os.path.abspath(os.path.join(basepath,  file_name))
  f = open(filepath, "r")
  return f

class TestCleaner(unittest.TestCase):

  def test_remove_repeated_lines(self):
    content = openrel("examples/2359-boilerplate.txt").read()
    [c2, removed_lines] = cleaner.remove_repeated_lines(content)
    self.assertEqual(len(c2),  645824)
#    print len(content), len(c2)
#    print "\n".join(removed_lines)

  def test_remove_intro1(self):
    content = openrel("examples/2359-boilerplate.txt").read()
    [c2, removed] = cleaner.remove_intro(content.lower())
#    print removed
#    print len(content), len(c2)
    self.assertEqual(len(c2),  631829)

  def test_remove_intro2(self):
#    content = open("examples/128.txt").read()
    
    [c2, removed] = cleaner.remove_intro("a\nuvod\nabc")
#    print removed
#    print len(content), len(c2)
#    print c2
    self.assertEqual(len(c2),  3)

  def test_fix_sumniki1(self):
    content = openrel("examples/sumniki-1.txt").read()
    [c2, removed] = cleaner.fix_sumniki(content)
    res = [ "RAČUNALNIŠTVO",
            "Andrej Šmuc",
            "Boštjančiču",
            "zaokrožen",
            "specifiika",
            "Gumb \"Show overlay\"",
            ]
    
    self.assertEqual(res, c2.split("\n"))

  def test_fix_sumniki2(self):
    content = openrel("examples/sumniki-2.txt").read()
    [c2, removed] = cleaner.fix_sumniki(content)
    res = [ "optično",
            "vpiše",
            "gšum",
            "optično",
            "vpiše",
            "gšum",
            "nic",
           ]
    
    self.assertEqual(res, c2.split("\n"))

  def test_fix_sumniki3(self):
    content = openrel("examples/sumniki-3.txt").read()
    [c2, removed] = cleaner.fix_sumniki(content)
    res = [ "Cimermančič",
            "S POMOČJO NAPREDNIH",
            "trženja mladim",
           ]
    
    self.assertEqual(res, c2.split("\n"))


if __name__ == '__main__':
    unittest.main()
