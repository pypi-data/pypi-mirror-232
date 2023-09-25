import importlib

PLUGIN_REGISTRY = {
    'PostgresPlugin': {
        'module': 'postgres_plugin.plugin',
        'class': 'PostgresPlugin'
    },
    'MySQLPlugin': {
        'module': 'mysql_plugin.plugin',
        'class': 'MySQLPlugin'
    },
    # Add more plugins as needed...
}

def plugin_factory(plugin_name, **kwargs):
    if plugin_name not in PLUGIN_REGISTRY:
        raise ValueError(f"Plugin {plugin_name} not found!")

    plugin_info = PLUGIN_REGISTRY[plugin_name]
    module = importlib.import_module(plugin_info['module'])
    plugin_class = getattr(module, plugin_info['class'])
    return plugin_class(**kwargs)
