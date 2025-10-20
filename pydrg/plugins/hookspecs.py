import pluggy

project_name = "pydrg"

hookspec = pluggy.HookspecMarker(project_name)
hookimpl = pluggy.HookimplMarker(project_name)


@hookspec
def client_load_classes(client):
    """
    Allow plugins to load/override additional Java classes on the given client.

    Plugins can set attributes on `client` (e.g., JClass handles) after core
    classes are loaded but before pricer/setup, if applicable. Return None.
    """


@hookspec
def client_methods(client):
    """
    Return a dict mapping method name -> callable to be bound as instance methods
    on the provided client.

    The callables should accept `self` as the first argument and will be bound with
    types.MethodType. Return an empty dict or None if not adding methods.
    """
