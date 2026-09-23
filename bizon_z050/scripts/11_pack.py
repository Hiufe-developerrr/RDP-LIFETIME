# 11 - make the saved .blend self-contained: pack every atlas texture into it
# at half resolution (4096 -> 2048, 2048 -> 1024; the full set would exceed
# GitHub's 100 MB file limit), so the file is not magenta when downloaded on
# its own. Image paths keep pointing at ../textures (full resolution): with
# the whole folder present, File > External Data > Unpack Resources >
# "Use files in original location" switches back to the 4096 files.
import os
import tempfile
import numpy as np

FACTOR = globals().get("FACTOR") or 2
scn = bpy.context.scene
fmt = scn.render.image_settings
prev_compression = fmt.compression
fmt.compression = 100                 # Image.save() takes the PNG zlib level from the scene
tmpdir = tempfile.mkdtemp(prefix="z050_pack_")
total = 0
for img in [im for im in D.images if im.source == 'FILE' and im.filepath]:
    w, h = img.size
    if w == 0:
        print("skip (file not found):", img.name)
        continue
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    a = px.reshape(h // FACTOR, FACTOR, w // FACTOR, FACTOR, 4).mean(axis=(1, 3))
    tmp = D.images.new("_pack_tmp", w // FACTOR, h // FACTOR, alpha=False)
    tmp.pixels.foreach_set(a.astype(np.float32).ravel())
    path = os.path.join(tmpdir, os.path.basename(bpy.path.abspath(img.filepath)))
    tmp.filepath_raw = path
    tmp.file_format = 'PNG'
    tmp.save()
    D.images.remove(tmp)
    with open(path, "rb") as f:
        data = f.read()
    # packing from memory keeps img.filepath; do not reload afterwards, a
    # reload re-reads the (full-size) file from that path
    img.pack(data=data, data_len=len(data))
    total += len(data)
    print(f"packed {img.name}: {w} -> {w // FACTOR} px, {len(data) / 1e6:.1f} MB")
fmt.compression = prev_compression
bpy.ops.wm.save_mainfile(compress=True)
print(f"saved {bpy.data.filepath}: {os.path.getsize(bpy.data.filepath) / 1e6:.1f} MB "
      f"(packed textures {total / 1e6:.1f} MB)")
