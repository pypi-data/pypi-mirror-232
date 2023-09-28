"""Handle image reading, writing and plotting plugins.

To improve performance, plugins are only loaded as needed. As a result, there
can be multiple states for a given plugin:

    available: Defined in an *ini file located in `pyzjr.io._plugins`.
        See also `pyzjr.io.available_plugins`.
    partial definition: Specified in an *ini file, but not defined in the
        corresponding plugin module. This will raise an error when loaded.
    available but not on this system: Defined in `pyzjr.io._plugins`, but
        a dependent library (e.g. Qt, PIL) is not available on your system.
        This will raise an error when loaded.
    loaded: The real availability is determined when it's explicitly loaded,
        either because it's one of the default plugins, or because it's
        loaded explicitly by the user.

"""
import os.path
import warnings
from configparser import ConfigParser
from glob import glob


__all__ = ['use_plugin', 'call_plugin', 'reset_plugins']

# The plugin store will save a list of *loaded* io functions for each io type
# (e.g. 'imread', 'imsave', etc.). Plugins are loaded as requested.
plugin_store = None
# Dictionary mapping plugin names to a list of functions they provide.
plugin_provides = {}
# The module names for the plugins in `pyzjr.io._plugins`.
plugin_module_name = {}
# Meta-data about plugins provided by *.ini files.
plugin_meta_data = {}
# For each plugin type, default to the first available plugin as defined by
# the following preferences.
preferred_plugins = {
    # Default plugins for all types (overridden by specific types below).
    'all': ['matplotlib'],
    'imshow': ['matplotlib'],
}


def _clear_plugins():
    """Clear the plugin state to the default, i.e., where no plugins are loaded
    """
    global plugin_store
    plugin_store = {'imread': [],
                    'imsave': [],
                    'imshow': []}
_clear_plugins()


def _load_preferred_plugins():
    # Load preferred plugin for each io function.
    io_types = ['imsave', 'imshow', 'imread']
    for p_type in io_types:
        _set_plugin(p_type, preferred_plugins['all'])

    plugin_types = (p for p in preferred_plugins.keys() if p != 'all')
    for p_type in plugin_types:
        _set_plugin(p_type, preferred_plugins[p_type])


def _set_plugin(plugin_type, plugin_list):
    for plugin in plugin_list:
        try:
            use_plugin(plugin, kind=plugin_type)
            break
        except (ImportError, RuntimeError, OSError):
            pass


def reset_plugins():
    _clear_plugins()
    _load_preferred_plugins()


def _parse_config_file(filename):
    """Return plugin name and meta-data dict from plugin config file."""
    parser = ConfigParser()
    parser.read(filename)
    name = parser.sections()[0]

    meta_data = {}
    for opt in parser.options(name):
        meta_data[opt] = parser.get(name, opt)

    return name, meta_data


def _scan_plugins():
    """Scan the plugins directory for .ini files and parse them
    to gather plugin meta-data.
    """
    pd = os.path.dirname(__file__)
    config_files = glob(os.path.join(pd, '_plugins', '*.ini'))

    for filename in config_files:
        name, meta_data = _parse_config_file(filename)
        if 'provides' not in meta_data:
            warnings.warn(f'file {filename} not recognized as a scikit-image io plugin, skipping.')
            continue
        plugin_meta_data[name] = meta_data
        provides = [s.strip() for s in meta_data['provides'].split(',')]
        valid_provides = [p for p in provides if p in plugin_store]

        for p in provides:
            if p not in plugin_store:
                print("Plugin `%s` wants to provide non-existent `%s`."
                      " Ignoring." % (name, p))


        plugin_provides[name] = valid_provides

        plugin_module_name[name] = os.path.basename(filename)[:-4]


_scan_plugins()


def call_plugin(kind, *args, **kwargs):
    """Find the appropriate plugin of 'kind' and execute it."""
    if kind not in plugin_store:
        raise ValueError('Invalid function (%s) requested.' % kind)

    plugin_funcs = plugin_store[kind]
    if len(plugin_funcs) == 0:
        msg = ("No suitable plugin registered for %s.\n\n"
               "You may load I/O plugins with the `pyzjr.io.use_plugin` "
               "command.  A list of all available plugins are shown in the "
               "`pyzjr.io` docstring.")
        raise RuntimeError(msg % kind)

    plugin = kwargs.pop('plugin', None)
    if plugin is None:
        _, func = plugin_funcs[0]
    else:
        _load(plugin)
        try:
            func = [f for (p, f) in plugin_funcs if p == plugin][0]
        except IndexError:
            raise RuntimeError('Could not find the plugin "%s" for %s.' %
                               (plugin, kind))

    return func(*args, **kwargs)


def use_plugin(name, kind=None):
    """Set the default plugin for a specified operation.  The plugin
    will be loaded if it hasn't been already.
    """
    if kind is None:
        kind = plugin_store.keys()
    else:
        if kind not in plugin_provides[name]:
            raise RuntimeError("Plugin %s does not support `%s`." %
                               (name, kind))

        if kind == 'imshow':
            kind = [kind]


    _load(name)

    for k in kind:
        if k not in plugin_store:
            raise RuntimeError("'%s' is not a known plugin function." % k)

        funcs = plugin_store[k]

        # Shuffle the plugins so that the requested plugin stands first
        # in line
        funcs = [(n, f) for (n, f) in funcs if n == name] + \
                [(n, f) for (n, f) in funcs if n != name]

        plugin_store[k] = funcs


def _load(plugin):
    """Load the given plugin.

    Parameters
    ----------
    plugin : str
        Name of plugin to load.

    See Also
    --------
    plugins : List of available plugins

    """
    if plugin not in plugin_module_name:
        raise ValueError("Plugin %s not found." % plugin)
    else:
        modname = plugin_module_name[plugin]
        plugin_module = __import__('pyzjr.core._plugins.' + modname,
                                   fromlist=[modname])

    provides = plugin_provides[plugin]
    for p in provides:

        if not hasattr(plugin_module, p):
            print("Plugin %s does not provide %s as advertised.  Ignoring." %
                  (plugin, p))
            continue

        store = plugin_store[p]
        func = getattr(plugin_module, p)
        if not (plugin, func) in store:
            store.append((plugin, func))




