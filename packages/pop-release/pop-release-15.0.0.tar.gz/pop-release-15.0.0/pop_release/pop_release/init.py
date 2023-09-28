def __init__(hub):
    hub.pop.sub.add(dyne_name="idem")
    hub.pop.sub.add(dyne_name="lib")
    hub.pop.sub.add(python_import="contextlib", sub=hub.lib)
    hub.pop.sub.add(python_import="glob", sub=hub.lib)
    hub.pop.sub.add(python_import="importlib", sub=hub.lib)
    hub.pop.sub.add(python_import="io", sub=hub.lib)
    hub.pop.sub.add(python_import="os", sub=hub.lib)
    hub.pop.sub.add(python_import="pathlib", sub=hub.lib)
    hub.pop.sub.add(python_import="shutil", sub=hub.lib)
    hub.pop.sub.add(python_import="subprocess", sub=hub.lib)
    hub.pop.sub.add(python_import="sys", sub=hub.lib)
    hub.pop.sub.add(python_import="twine", sub=hub.lib)
    hub.lib.importlib.import_module("twine.commands.check")
    hub.lib.importlib.import_module("twine.commands.register")
    hub.lib.importlib.import_module("twine.commands.upload")
    hub.lib.importlib.import_module("twine.settings")
    hub.lib.importlib.import_module("twine.utils")


def cli(hub):
    hub.pop.config.load(["pop_release", "idem", "acct"], cli="pop_release")

    print(hub.OPT.acct)
    hub.pop.loop.create()
    hub.pop.Loop.run_until_complete(
        hub.pop_release.cli.run(
            root_path=hub.lib.pathlib.Path(hub.OPT.pop_release.root),
            version=hub.OPT.pop_release.ver,
            skip=hub.OPT.pop_release.skip,
            remote=hub.OPT.pop_release.remote,
            acct_file=hub.OPT.acct.acct_file,
            acct_key=hub.OPT.acct.acct_key,
            acct_profile=hub.OPT.idem.acct_profile,
        )
    )
