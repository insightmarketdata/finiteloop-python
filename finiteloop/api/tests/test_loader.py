import unittest
import inspect
import os
from finiteloop.api.loader import ModuleInspector
from finiteloop.api.loader import FindResources
from finiteloop.api.loader import GetApiUrls

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


class TestFindResources(unittest.TestCase):

    def setUp(self):
        apps = ['finiteloop.resourcetester']
        self.obj = FindResources(apps)

    def test_all(self):
        self.assertIsNotNone(self.obj.all)

    def test_all_is_list(self):
        self.assertIsInstance(self.obj.all, list)

    def test_length(self):
        self.assertEqual(len(self.obj.all), 1)

    def test_is_resource(self):
        mod = self.obj.all[0]
        msg = "{} is not correct".format(mod.name)
        self.assertTrue(mod.name.endswith('TrustyResource'), msg)


class MockTastyPieApiObj(object):

    def __init__(self):
        self.urls = []

    def register(self, name):
        self.urls.append(name)


class TestApiUrls(unittest.TestCase):

    def setUp(self):
        self.obj = GetApiUrls(MockTastyPieApiObj())

    def test_urls(self):
        objs = ['one', 'two', 'three']
        self.obj.add(objs)
        self.assertEquals(self.obj.urls(), objs)




