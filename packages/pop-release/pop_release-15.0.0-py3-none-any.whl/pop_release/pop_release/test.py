def __virtual__(hub):
    try:
        hub.pop.sub.add(python_import="pytest", sub=hub.lib)
        return (True,)
    except ImportError as e:
        hub.log.trace(f"Skipping pytest phases of pop-release: {e}")
        return False, str(e)


def pytest(hub, root_dir: "pathlib.Path"):
    """
    Run pytest and fail the sequence if pytest fails
    """
    retcode = hub.lib.pytest.main([str(root_dir / "tests"), "--color=yes", "--quiet"])
    if retcode == 5:
        # No tests, skip
        hub.log.warning("This project has no tests")
        return
    if retcode:
        raise ChildProcessError(f"Pytest failed: {retcode}")
