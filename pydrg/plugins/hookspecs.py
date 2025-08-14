import pluggy


project_name = "pydrg"

hookspec = pluggy.HookspecMarker(project_name)
hookimpl = pluggy.HookimplMarker(project_name)


@hookspec
def ipps_load_classes(ipps_client):
    """
    Allow plugins to load/override additional Java classes on the given IPPS client.

    Plugins can set attributes on `ipps_client` (e.g., JClass handles) after core
    classes are loaded but before pricer setup. Return None.
    """


@hookspec
def ipps_client_methods(ipps_client):
    """
    Return a dict mapping method name -> callable to be bound as instance methods
    on the provided IPPS client.

    The callables should accept `self` as the first argument and will be bound with
    types.MethodType. Return an empty dict or None if not adding methods.
    """


