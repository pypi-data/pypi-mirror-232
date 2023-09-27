def gather(hub, profiles):
    sub_profiles = {}
    for name, ctx in profiles.get("twine", {}).items():
        sub_profiles[name] = {
            "settings": hub.lib.twine.settings.Settings(non_interactive=True, **ctx)
        }
    return sub_profiles
