import bpy
import os

# dir_render = os.path.abspath(r"F:\ARM\3D\2021\TolkiensWorld\build\prpGlobeA\shd\renders\turntables\v001")
# resolution = "1080,1080"
# res_x, res_y = [int(x) for x in resolution.split(",")]
# view_transform = "Rec.709"

dir_render = os.getenv("proxy_dir_render")
resolution = os.getenv("proxy_resolution")
view_transform = os.getenv("proxy_view_transform")
mdl_var = os.getenv("proxy_mdl_var")
txt_var = os.getenv("proxy_txt_var")
asset = os.getenv('PIPE_ASSET')

res_x, res_y = [int(x) for x in resolution.split(",")]


def import_image(dir_render, imgs_render):
    filepath = os.path.join(dir_render, imgs_render[0])
    dict_files = [{"name": texture} for texture in imgs_render]
    bpy.ops.image.open(filepath=filepath, directory=dir_render, files=dict_files, show_multiview=False,
                       use_sequence_detection=True, use_udim_detecting=False)
    img = [x for x in bpy.data.images if x.name not in ["Render Result", "Viewer Node"]][0]
    return img


# import image sequence
files_render = os.listdir(dir_render)
filetypes = []
for file in files_render:
    filetype = file.split(".")[-1]
    if filetype not in filetypes:
        filetypes.append(filetype)
if "exr" in filetypes:
    print('a')
    imgs_render = [x for x in files_render if x.split(".")[-1] == "exr"]
elif "png" in filetypes:
    imgs_render = [x for x in files_render if x.split(".")[-1] == "png"]
elif "jpg" in filetypes:
    imgs_render = [x for x in files_render if x.split(".")[-1] == "jpg"]
else:
    imgs_render = []


if imgs_render:
    img = import_image(dir_render, imgs_render)
    frames = [int(x.split(".")[-2]) for x in imgs_render]
    frames.sort()
    length = frames[-1] - frames[0] + 1
    print(img.name)
    print(frames)

    bpy.context.scene.frame_start = frames[0]
    bpy.context.scene.frame_end = frames[-1]

    # Generate node tree
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    render = tree.nodes['Render Layers']
    tree.nodes.remove(render)

    image_node = tree.nodes.new(type="CompositorNodeImage")
    image_node.image = img
    image_node.layer = mdl_var
    image_node.location = 0, 400
    image_node.frame_duration = length
    # image_node.image = bpy.data.images[]
    output_node = tree.nodes['Composite']

    link = tree.links.new(image_node.outputs[0], output_node.inputs[0])

    # Settings
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y

    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'

    version = os.path.split(dir_render)[-1]
    fl_out = os.path.join(dir_render, f"{asset}.{mdl_var}v{txt_var}.{version}.proxy.mp4")
    bpy.context.scene.render.filepath = fl_out
    bpy.context.scene.view_settings.view_transform = view_transform

    bpy.ops.render.render(animation=True)
