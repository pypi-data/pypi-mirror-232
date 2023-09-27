def patch(hub, ctx: dict):
    """
    Patch ctx.acct so that it has appropriate twine settings
    """
    if "acct" not in ctx:
        return ctx
    
    ctx.acct.settings = hub.lib.twine.settings.Settings(
        **ctx.acct,
        non_interactive=True,
        verbose=True,
        disable_progress_bar=True,
        )
