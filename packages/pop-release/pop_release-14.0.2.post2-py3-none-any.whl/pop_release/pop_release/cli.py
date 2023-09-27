from typing import List


async def run(
    hub,
    version,
    root_path: "pathlib.Path",
    skip: List[str],
    remote: str,
    acct_file: str,
    acct_key: str,
    acct_profile: str,
):
    if skip is None:
        print("Running full release process")
        skip = []
    print(f"Working directory: {root_path}")
    print("Generating ctx")
    validate_profile = "release" not in skip
    print(f"{'not 'if not validate_profile else ''}validating profile {acct_profile}")
    
    ctx = await hub.idem.acct.ctx(
        "exec.twine.",
        acct_file=acct_file,
        acct_key=acct_key,
        profile=acct_profile,
        hard_fail=validate_profile,
        validate=validate_profile,
    )

    hub.pop_release.settings.patch(ctx)

    if version and "version" not in skip:
        if "coerce" not in skip and "sv" in hub.pop_release._loaded:
            print("Coercing the version number to semantic style")
            version = hub.pop_release.sv.coerce(str(version))
            print("Updating release version")
        hub.pop_release.version.set_ver(root_path, version)
        print("Updating docs version")
        hub.pop_release.version.set_doc(root_path, version)
    if "test" not in skip and "test" in hub.pop_release._loaded:
        print("Running tests")
        hub.pop_release.test.pytest(root_path)
    if "git" not in skip and "git" in hub.pop_release._loaded:
        if "commit" not in skip:
            print("Committing changes")
            hub.pop_release.git.commit(root_path, version)
        if "tag" not in skip:
            print("Tagging commit")
            hub.pop_release.git.tag(root_path, version)
    if "clean" not in skip:
        print("Cleaning up")
        hub.pop_release.dist.clean(root_path)
    if "build" not in skip:
        print("Building dist files")
        hub.pop_release.dist.build(root_path)
    if not ctx.acct or not validate_profile:
        print("No twine credentials found, skipping release process")
        choice = "n"
    elif "input" in skip:
        choice = "y"
    else:
        git_prompt = " git and to " if "git" not in skip else " "

        try:
            choice = input(
                f"Build for version {version} is complete, Push to{git_prompt}{ctx.acct.settings.repository_config['repository']}? [Y,n] "
            )
        except KeyboardInterrupt:
            choice = "n"

    if not choice or choice.lower().startswith("y"):
        if "release" not in skip:
            print("Releasing to repository")
            await hub.pop_release.twine.push(ctx, root_path)
        if (
            "push" not in skip
            and "git" not in skip
            and "git" in hub.pop_release._loaded
        ):
            print(f"Pushing to git remote: {remote}")
            hub.pop_release.git.push(root_path, remote)

    print("Success!")
