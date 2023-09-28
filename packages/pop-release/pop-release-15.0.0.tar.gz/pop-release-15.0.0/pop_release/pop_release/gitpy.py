__virtualname__ = "git"


def __virtual__(hub):
    try:
        hub.pop.sub.add(python_import="git", sub=hub.lib)
        return (True,)
    except ImportError as e:
        hub.log.trace(f"Skipping git-based phases of pop-release: {e}")
        return False, str(e)


def commit(hub, git_root: str, version: str):
    """
    Commit the given changes to git
    """
    repo = hub.lib.git.Repo(git_root, search_parent_directories=True)
    repo.git.add(update=True)
    repo.index.commit(f'"Version bump to {version}"')


def tag(hub, git_root: str, version: str):
    """
    Set the tag
    """
    repo = hub.lib.git.Repo(git_root, search_parent_directories=True)
    repo.create_tag(f"v{version}", ref="HEAD", message=f"Version {version}", force=True)


def push(hub, git_root: str, remote: str = "origin"):
    """
    Push the changes
    """
    repo = hub.lib.git.Repo(git_root, search_parent_directories=True)
    origin: hub.lib.git.Remote = repo.remotes[remote]
    origin.fetch()
    origin.push(repo.active_branch.name)
