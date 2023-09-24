"""
Test the example with the STL mesher.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

from tests import test_workflow
from pypeec import main

# example folder to be tested
folder = "examples_stl"

# name of the examples
name_list = [
    "inductor_air",
    "inductor_core",
    "transformer",
]

# show the logo
main.run_hide_logo()

# get the test object
obj = test_workflow.set_init()

# add the tests
for name in name_list:
    test_workflow.set_test(obj, folder, name)
