import unittest
import inspect
import os
from finiteloop.api.loader import ModuleInspector


class TestModuleInspectorAsEgg(unittest.TestCase):

    def setUp(self):
        self.obj = ModuleInspector('setuptools')

    def test_mod(self):
        self.assertIsNotNone(self.obj.mod)

    def test_mod_is_setuptools(self):
        self.assertTrue(inspect.ismodule(self.obj.mod))

    def test_type(self):
        self.assertEqual(ModuleInspector.EGG, self.obj.type)

    def test_mod_path(self):
        self.assertTrue(self.obj.mod_path.endswith('/'))

    def test_has_submodules(self):
        path, filename = os.path.split(self.obj.mod.__file__)
        self.assertTrue(self.obj._has_submodules(filename))

    def test_sub_modules(self):
        out = self.obj.sub_modules()
        self.assertIsInstance(out, list)


class TestModuleInspectorAsLocal(unittest.TestCase):

    def setUp(self):
        self.obj = ModuleInspector('finiteloop')

    def test_mod(self):
        self.assertIsNotNone(self.obj.mod)

    def test_mod_is_finiteloop(self):
        self.assertTrue(inspect.ismodule(self.obj.mod))

    def test_type(self):
        self.assertEqual(ModuleInspector.LOCAL, self.obj.type)

    def test_mod_path(self):
        self.assertTrue(self.obj.mod_path.endswith('/'))

    def test_has_submodules(self):
        path, filename = os.path.split(self.obj.mod.__file__)
        self.assertTrue(self.obj._has_submodules(filename))

    def test_sub_modules(self):
        out = self.obj.sub_modules()
        self.assertIsInstance(out, list)
