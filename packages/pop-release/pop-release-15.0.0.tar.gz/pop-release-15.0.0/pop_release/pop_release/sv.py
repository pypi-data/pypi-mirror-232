def __virtual__(hub):
    try:
        hub.pop.sub.add(python_import="semantic_version", sub=hub.lib)
        return (True,)
    except ImportError as e:
        hub.log.trace(f"Skipping version-coercion phase of pop-release: {e}")
        return False, str(e)


def coerce(hub, version: str) -> str:
    return str(hub.lib.semantic_version.Version.coerce(str(version)))
