import twine.settings

def get(hub, ctx):
    """
    Transform ctx.acct into twine settings object
    """
    return {"result": True, "ret": twine.settings.Settings(non_interactive=True, **ctx.acct, verbose=True, disable_progress_bar=True), "comment": ""}
    