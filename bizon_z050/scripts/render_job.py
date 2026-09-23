# Renders the listed cameras with Cycles from a timer (so the MCP call returns
# immediately); progress goes to <out>/render_status.txt.
import os
import time

JOB = globals().get("JOB") or {"cams": ["cam_front_left"], "res": (1600, 900), "samples": 96,
                               "out": "/tmp/hoplite/workspace/bizon_z050/renders", "suffix": ""}


def _run():
    scn = bpy.context.scene
    os.makedirs(JOB["out"], exist_ok=True)
    status = os.path.join(JOB["out"], "render_status.txt")
    scn.render.engine = 'CYCLES'
    scn.cycles.samples = JOB["samples"]
    scn.cycles.use_denoising = True
    scn.render.resolution_x, scn.render.resolution_y = JOB["res"]
    scn.render.resolution_percentage = 100
    scn.render.image_settings.file_format = 'PNG'
    for name in JOB["cams"]:
        t0 = time.time()
        scn.camera = D.objects[name]
        scn.render.filepath = os.path.join(JOB["out"], name.replace("cam_", "") + JOB["suffix"] + ".png")
        bpy.ops.render.render(write_still=True)
        with open(status, "a") as f:
            f.write(f"{name} done in {time.time() - t0:.0f}s -> {scn.render.filepath}\n")
    with open(status, "a") as f:
        f.write("ALL DONE\n")
    return None


os.makedirs(JOB["out"], exist_ok=True)
open(os.path.join(JOB["out"], "render_status.txt"), "w").write("started\n")
bpy.app.timers.register(_run, first_interval=0.5)
print("render job queued:", JOB)
