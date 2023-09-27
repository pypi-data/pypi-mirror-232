"""Made this class since I tired to write some dir setup code for every unittest"""
import sys
import os

from shutil import rmtree
from unittest import TestCase

from ceotr_common_utilities.file_prepare.file_prepare import check_create_dir


class TestBaseMetaclass(type):
    def __new__(cls, name, bases, dct):
        dct["resource_dir"] = None
        dct["output_dir"] = None
        return super().__new__(cls, name, bases, dct)


class TestBase(TestCase, metaclass=TestBaseMetaclass):

    def _set_up_resource_dir(self):
        self.resource_dir = check_create_dir(
            os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), 'resource'))

    def _set_up_output_dir(self):
        self.output_dir = check_create_dir(
            os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), 'output'))

    def _clear_output_dir(self):
        dir_list = os.listdir(self.output_dir)
        for file in dir_list:
            path = os.path.join(self.output_dir, file)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                rmtree(path)

    def base_setup(self):
        self._set_up_resource_dir()
        self._set_up_output_dir()

    def clear_up(self):
        # clean the file under output dir, but not output dir itself
        self._clear_output_dir()

    def __getattr__(self, item):
        ignore = ['base_setup', 'resource_dir', 'output_dir']
        if item not in ignore:
            if self.resource_dir is None or self.output_dir is None:
                self.base_setup()
        return self.__getattribute__(item)
