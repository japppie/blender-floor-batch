import bpy
import csv
import os

csv_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/assets/demo_floors.csv'
with open(csv_location) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')


material_name = 'floor'
mat = bpy.data.materials[material_name]
nodes = mat.node_tree.nodes
image_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/data/'
image = '470068_id.jpg' 
output_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/output/'
output_name = image.split('_')[0] + '.jpg'
full_output_path = os.path.join(output_location, output_name)
#image = 'test_id.png' 


# Iterate through the nodes and update the image paths
def update_textures():
    for i in range(1, 11):
        node_name = f'tex{i:02}'
        image_path = os.path.join(image_location, image.replace('id', str(i)))

        # Check if node exists and is an image texture node
        node = nodes.get(node_name)
        if node and node.type == 'TEX_IMAGE':
            if os.path.exists(image_path):
                new_image = bpy.data.images.load(image_path, check_existing=True)
                node.image = new_image
                node.image.reload()
                print(f'Updated {node_name} with {image_path}')
            else:
                print(f'Image file not found: {image_path}')
        elif node:
            print(f'Node {node_name} is not an image texture node.')
        else:
            print(f'Node {node_name} not found.')




update_textures()

# Set the camera
camera = bpy.data.objects.get('MAIN_CAMERA')
if camera and camera.type == 'CAMERA':
    bpy.context.scene.camera = camera
else:
    print('MAIN_CAMERA not found or is not a camera object.')

# Render the scene
bpy.context.scene.render.filepath = full_output_path
print(f'Rendering to {full_output_path}...')
bpy.ops.render.render(write_still=True)