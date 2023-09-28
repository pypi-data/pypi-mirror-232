def pre(hub, ctx):
    if "ctx" in ctx.signature.parameters:
        func_ctx = ctx.args[1]
        hub.pop_release.settings.patch(func_ctx)
