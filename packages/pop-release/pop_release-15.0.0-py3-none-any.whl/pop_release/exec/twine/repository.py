__virtualname__ = "repo"


async def check(hub, ctx):
    try:
        with hub.lib.io.StringIO() as f:
            with hub.lib.contextlib.redirect_stdout(f):
                ctx.acct.settings.check_repository_url()
                return {"result": True, "ret": f.getvalue(), "comment": None}
    except Exception as e:
        return {"result": False, "ret": str(e), "comment": e.__class__}


async def create(hub, ctx):
    ctx.acct.settings.create_repository()
