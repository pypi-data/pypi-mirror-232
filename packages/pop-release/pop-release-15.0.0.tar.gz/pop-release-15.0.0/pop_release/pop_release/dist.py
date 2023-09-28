def clean(hub, root_dir: "pathlib.Path"):
    """
    clean everything up
    """
    ret = hub.lib.subprocess.run(
        [
            hub.lib.sys.executable,
            str(root_dir / "setup.py"),
            "--no-user-cfg",
            "--quiet",
            "clean",
        ]
    )
    ret.check_returncode()
    try:
        hub.lib.shutil.rmtree(str(root_dir / "dist"))
    except FileNotFoundError:
        ...


def build(hub, root_dir: "pathlib.Path"):
    """
    Build the release
    """
    ret = hub.lib.subprocess.run(
        [
            hub.lib.sys.executable,
            str(root_dir / "setup.py"),
            "--no-user-cfg",
            "--quiet",
            "sdist",
            "bdist_wheel",
        ],
    )
    ret.check_returncode()
