"""MCP stdio client that drives Blender through the mcp-for-blender server
(tool: execute_blender_code). Connection: BLENDER_HOST / BLENDER_PORT
(defaults 127.0.0.1:9876).

  python mcp_client.py --lib lib.py --code 02_chassis.py [--code ...]
  python mcp_client.py --tool get_scene_info
  python mcp_client.py --tool get_viewport_screenshot --out shot.png
"""
import argparse, asyncio, base64, json, os, shutil, sys, time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

USER_PROMPT = ("Użyj dostępnego narzędzia MCP Blendera (blender MCP), aby zbudować trójwymiarowy "
               "model kombajnu Bizon Z050 Super bezpośrednio w połączonym programie Blender.")


def server_cmd():
    exe = shutil.which("mcp-for-blender") or os.path.expanduser("~/.local/bin/mcp-for-blender")
    return (exe, []) if os.path.exists(exe) else ("uvx", ["mcp-for-blender"])


async def main(ns):
    failed = False
    env = dict(os.environ)
    env.setdefault("BLENDER_HOST", "127.0.0.1")
    env.setdefault("BLENDER_PORT", "9876")
    env["DISABLE_TELEMETRY"] = "true"
    cmd, args = server_cmd()
    params = StdioServerParameters(command=cmd, args=args, env=env)
    lib = open(ns.lib, encoding="utf-8").read() + "\n" if ns.lib else ""
    async with stdio_client(params, errlog=open(os.devnull, "w")) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            for path in ns.code or []:
                code = lib + open(path, encoding="utf-8").read()
                t0 = time.time()
                res = await s.call_tool("execute_blender_code", {"code": code, "user_prompt": USER_PROMPT})
                text = "\n".join(getattr(c, "text", "") for c in res.content)
                print(f"### {os.path.basename(path)} ({time.time() - t0:.1f}s)\n{text}", flush=True)
                if text.startswith("Error executing code") or res.isError:
                    failed = True
                    break
            if ns.tool:
                targs = json.loads(ns.args) if ns.args else {}
                targs.setdefault("user_prompt", USER_PROMPT)
                res = await s.call_tool(ns.tool, targs)
                for c in res.content:
                    if getattr(c, "type", "") == "image":
                        out = ns.out or "mcp_image.png"
                        open(out, "wb").write(base64.b64decode(c.data))
                        print("image saved to", out)
                    else:
                        print(getattr(c, "text", c))
    return 2 if failed else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--lib")
    p.add_argument("--code", action="append")
    p.add_argument("--tool")
    p.add_argument("--args")
    p.add_argument("--out")
    sys.exit(asyncio.run(main(p.parse_args())))
