def get_version() -> str:

    from importlib_metadata import version
    return version('ness_search')