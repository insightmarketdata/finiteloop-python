import os
import zipfile
import zipimport
import inspect
from collections import namedtuple

class ModuleInspector(object):
    """used to find any submodules a module may have
    """

    LOCAL = 'local'
    EGG = 'egg'

    def __init__(self, name):
        """Used to find any sub-modules a module may have
        :param name: module name with dot separators if applicable
        """
        self.name = name
        self._mod = None
        self._type = None
        self._zip = None
        self._zip_file = None
        self._mod_path = None

    @property
    def mod(self):
        """The actual module
        """
        if not self._mod:
            try:
                from django.utils.importlib import import_module
            except ImportError:
                from importlib import import_module

            self._mod = import_module(self.name)
        return self._mod

    @property
    def type(self):
        """Lets us know if the module is from the
        filesystem (local) or from an egg
        """
        if not self._type:
            try:
                self._zip = zipimport.zipimporter(self.mod.__file__)
            except zipimport.ZipImportError:
                self._type = self.LOCAL
            else:
                self._zip_file = zipfile.ZipFile(self._zip.archive)
                self._type = self.EGG
        return self._type

    @property
    def mod_path(self):
        """the module name changed from dot notation to filesystem notation
        """
        if not self._mod_path:
            self._mod_path = self.name.replace('.', '/')
            self._mod_path = "{}/".format(self._mod_path)
        return self._mod_path

    def _has_submodules(self, filename):
        """Returns True if the module could have submodules
        """
        if filename.startswith('__init__'):
            return True
        else:
            return False

    def sub_modules(self):
        """Returns a list of sub-module names
        """
        out = []
        path, filename = os.path.split(self.mod.__file__)
        if self._has_submodules(filename):
            if self.type == self.LOCAL:
                out = self._find_local_submods(path)
            elif self.type == self.EGG:
                out = self._find_egg_submods()
        return out

    def _find_egg_submods(self):
        """Finds and returns a list of the sub-module names that exist
        inside and egg
        """
        out = set()
        for path in self._zip_file.namelist():
            name = path.partition(self.mod_path)[2]
            if name:
                name = name.split('/')[0]
                name = os.path.splitext(name)[0]
                if not name.startswith('__'):
                    out.add("{}.{}".format(self.name, name))
        return sorted(out)

    def _find_local_submods(self, path):
        """Finds and returns a list of the sub-module names that exist
        on the filesystem.
        :param path: the path to the module
        """
        out = set()
        for root, dirs, files in os.walk(path):
            for name in files:
                name = os.path.splitext(name)[0]
                if not name.startswith('__'):
                    out.add("{}.{}".format(self.name, name))
        return sorted(out)


class FindResources(object):
    """Object that will inspect Django applications looking for
    `resources` modules that contain Tastypie Resources.
    """

    """ Applications that will automatically be ignored
    """
    IGNORE = ('django', 'south', 'tastypie',)

    """ Methods on a resource object that designatate it as a
    Tasty Pie object
    """
    SIGNATURE = ('hydrate', 'dehydrate',)

    """ Fields for building a named tuple
    """
    FIELDS = ('name', 'obj',)

    def __init__(self, apps):
        self._apps = apps
        self._resources = []
        self._build_mod = namedtuple('mod', 'mod, name')
        self._build_resource = namedtuple('res', 'name, obj')

    @classmethod
    def load(cls):
        from django.conf import settings
        return cls(settings.INSTALLED_APPS)

    @property
    def all(self):
        if not self._resources:
            self._resources = self._get_resources()
        return self._resources

    def __iter__(self):
        for resource in self.all:
            print resource.name
            yield resource.obj()

    def _get_resources(self):
        out = []
        for app in self._get_app_mods():
            for name in dir(app.mod):
                if name.endswith('Resource'):
                    obj = getattr(app.mod, name)
                    if self._is_resource_object(app.name, obj):
                        name = "{}.{}".format(app.name, name)
                        out.append(self._build_resource(name, obj))
        return out

    def _get_apps(self):
        """Returns a list of appliation names
        """
        return [app_name for app_name in self._apps if self._should_process(app_name)]

    def _should_process(self, app_name):
        """ Returns true if the given app_name should be processed
        """
        for name in self.IGNORE:
            if app_name.lower().find(name.lower()) > -1:
                return False
        return True

    def _get_app_mods(self):
        out = []
        for app in self._get_apps():
            app = "{}.resources".format(app)
            self._get_mods(app, out)
        return out

    def _get_mods(self, name, hold):
        obj = ModuleInspector(name)
        try:
            mod = obj.mod
        except ImportError:
            pass
        else:
            hold.append(self._build_mod(mod, obj.name))
            for name in obj.sub_modules():
                self._get_mods(name, hold)

    def _is_resource_object(self, app_name, obj):
        if obj:
            if self._is_tastpie_resource(obj):
                if obj.__module__.startswith(app_name):
                    return True
        return False

    def _is_tastpie_resource(self, obj):
        if inspect.isclass(obj):
            for name in self.SIGNATURE:
                if not hasattr(obj, name):
                    return False
            return True
        return False


class ApiUrls(object):

    API_NAME = 'api'

    def __init__(self, tasty_pie_api_obj):
        self._tasty_pie_api_object = tasty_pie_api_obj

    def add(self, resrouce_objects):
        for obj in resrouce_objects:
            self._tasty_pie_api_object.register(obj)

    def urls(self):
        return self._tasty_pie_api_object.urls

    @classmethod
    def load(cls, api_name=None, resources=None):
        api_name = api_name or cls.API_NAME

        from django.conf import settings
        resources = resources or FindResources(settings.INSTALLED_APPS)

        from tastypie.api import Api as TastyPieApi
        tasty_pie_api_obj = TastyPieApi(api_name=api_name)

        get_all = cls(tasty_pie_api_obj)
        get_all.add(resources)
        return get_all.urls()
