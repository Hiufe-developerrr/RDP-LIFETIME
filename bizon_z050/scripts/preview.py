# Quick Workbench previews (material colours) from fixed angles into _scratch/.
import os
OUT = "/tmp/hoplite/workspace/_scratch"
os.makedirs(OUT, exist_ok=True)
scn = bpy.context.scene
prev_engine = scn.render.engine
scn.render.engine = 'BLENDER_WORKBENCH'
sh = scn.display.shading
sh.light = 'STUDIO'
sh.color_type = 'MATERIAL'
sh.show_cavity = True
sh.cavity_type = 'WORLD'
sh.show_object_outline = True
scn.render.resolution_x, scn.render.resolution_y = 1280, 720
cam_data = D.cameras.get("_preview_cam") or D.cameras.new("_preview_cam")
cam = D.objects.get("_preview_cam") or D.objects.new("_preview_cam", cam_data)
if cam.name not in scn.collection.objects:
    scn.collection.objects.link(cam)
cam_data.lens = 40
prev_cam = scn.camera
scn.camera = cam
VIEWS = globals().get("VIEWS") or {
    "front_left": ((9.5, -10.5, 4.6), (0.0, 0.8, 1.5)),
    "rear_right": ((-9.0, 12.5, 4.8), (0.0, 1.5, 1.5)),
    "left": ((14.5, 1.0, 1.9), (0.0, 1.0, 1.7)),
}
for name, (loc, target) in VIEWS.items():
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scn.render.filepath = os.path.join(OUT, "prev_" + name + ".png")
    bpy.ops.render.render(write_still=True)
    print("wrote", scn.render.filepath)
scn.camera = prev_cam
scn.render.engine = prev_engine
scn.render.resolution_x, scn.render.resolution_y = 1600, 900
