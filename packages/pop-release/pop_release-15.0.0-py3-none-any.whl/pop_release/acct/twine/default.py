def gather(hub, profiles):
    """
    Gather a default profile from ~/.pypirc if none was provided
    """
    new_profiles = {}

    # If there are no twine profiles then get them from pypirc
    if not profiles.get("twine", {}):
        pypirc = hub.lib.os.path.expanduser("~/.pypirc")
        if hub.lib.os.path.exists(pypirc):
            twine_profiles = hub.lib.twine.utils.get_config(pypirc)
            for profile_name, ctx in twine_profiles.items():
                ctx["repository_name"] = profile_name
                new_profiles[profile_name] = ctx
                hub.log.debug(f"Added acct_profile from pypirc: {profile_name}")

    return new_profiles
