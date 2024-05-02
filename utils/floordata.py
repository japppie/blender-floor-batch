import os, bpy

class Floordata():
    def __init__(self, sku, size, pattern, grout, suffix, image_location, scene):
        self.sku = sku
        self.size_x, self.size_y = self.extract_size(size)
        self.pattern = pattern
        self.grout = grout
        self.suffix = suffix
        self.filenames = []
        self.scene = scene
        self.texture_count = self.count_textures(image_location)  # Automatically count textures

    def extract_size(self, size):
        size = size.replace(' x ', 'x').replace(',', '.')
        size_parts = size.split('x')
        if len(size_parts) == 2:
            try:
                size_x = float(size_parts[0].strip())
                size_y = float(size_parts[1].strip())
                return size_x, size_y
            except ValueError:
                print("Invalid number format:", size)
                return None, None
        else:
            return None, None

    def count_textures(self, image_location):
        texture_count = 0
        for file in os.listdir(image_location):
            if self.sku in file:
                texture_count += 1
                self.filenames.append(file)
                # print(f"Found texture: {file}")
        return int(texture_count)
    
class BlenderFloorProcessor:
    def __init__(self, camera_name, image_location, output_location):
        self.camera_name = camera_name
        self.image_location = image_location
        self.output_location = output_location

    def set_pattern(self, floor):
        obj_regular = 'Standard_4.0+'
        mat_regular = 'Floor_MultiTexture_Sherwood-Oak'
        obj_herringbone = 'Herringbone'
        mat_herringbone = 'Floor_MultiTexture_Inca-Carpenter-Oak'
        if floor.pattern in writing_variations['laminate_regular'] or '':
            return obj_regular, mat_regular
        elif floor.pattern in writing_variations['laminate_herringbone']:
            return obj_herringbone, mat_herringbone
        else:
            print(f'PATTERN FOR {floor.sku} NOT RECOGNIZED')

    def set_textures(self, floor):
        object_name, material_name = self.set_pattern(floor)
        mat = bpy.data.materials[material_name]
        nodes = mat.node_tree.nodes

        # Define the specific order of node names
        node_names = [
            "Image Texture", 
            "Image Texture.001", 
            "Image Texture.002", 
            "Image Texture.003", 
            "Image Texture.004", 
            "Image Texture.007", 
            "Image Texture.005", 
            "Image Texture.008"
        ]

        # Ensure there are enough filenames to match the nodes
        if len(floor.filenames) > len(node_names):
            print(f"More filenames than expected nodes. Some textures won't be used.")
            floor.filenames = floor.filenames[:len(node_names)]

        # Loop over filenames and corresponding node names
        for filename, node_name in zip(floor.filenames, node_names):
            image_path = os.path.join(self.image_location, filename)
            node = nodes.get(node_name)
            if node and node.type == 'TEX_IMAGE':
                if os.path.exists(image_path):
                    new_image = bpy.data.images.load(image_path, check_existing=True)
                    node.image = new_image
                    node.image.reload()
                    # print(f'Updated {node_name} with {image_path}')
                else:
                    print(f'Image file not found: {image_path}')
            elif node:
                print(f'Node {node_name} is not an image texture node.')
            else:
                print(f'Node {node_name} not found.')

        # Find the MultiTexture group node and the Reroute node
        multi_texture_node = next((node for node in nodes if node.type == 'GROUP' and node.label == 'MultiTexture'), None)
        reroute_node = nodes.get('Reroute.001')

        if not multi_texture_node or not reroute_node:
            print("MultiTexture group node or Reroute.001 node not found.")
            return

        # Connect the last texture node to the Reroute node after all textures are set
        if len(floor.filenames) > 0 and len(multi_texture_node.outputs) >= len(floor.filenames):
            link = mat.node_tree.links.new
            link(multi_texture_node.outputs[len(floor.filenames) - 1], reroute_node.inputs[0])
        else:
            print("Not enough outputs in MultiTexture node or no textures specified.")

    def set_size(self, floor):
        object_name, material_name = self.set_pattern(floor)
        obj = bpy.data.objects.get(object_name)
        if obj and 'GeometryNodes' in obj.modifiers:
            modifier = obj.modifiers["GeometryNodes"]
            modifier["Input_2"] = floor.size_x / 100
            modifier["Socket_0"] = floor.size_x / 100
            modifier["Input_3"] = floor.size_y / 100
            modifier["Socket_3"] = floor.size_y / 100
        else:
            print(f"Object '{object_name}' not found or it doesn't have a 'GeometryNodes' modifier.")

    def set_objects(self, floor):
        regular_obj = bpy.data.objects.get('Standard_4.0+')
        herringbone_obj = bpy.data.objects.get('Herringbone')
        if floor.pattern in writing_variations['laminate_regular'] or '':
            regular_obj.hide_render = False
            herringbone_obj.hide_render = True
        elif floor.pattern in writing_variations['laminate_herringbone']:
            regular_obj.hide_render = True
            herringbone_obj.hide_render = False
        else:
            print(f'Floor pattern for {floor.sku} not recognized' )

    def set_camera(self):
        camera = bpy.data.objects.get(self.camera_name)
        if camera and camera.type == 'CAMERA':
            bpy.context.scene.camera = camera
        else:
            print(f'{self.camera_name} not found or is not a camera object.')

    def render_scene(self, floor):
        self.set_camera()
        full_output_path = os.path.join(self.output_location, floor.sku + floor.suffix)
        bpy.context.scene.render.filepath = full_output_path
        bpy.ops.render.render(write_still=True)
        # print(f'Rendering {floor.sku} to {full_output_path}')

    def batch_process(self, render_floordata):
        for floor in render_floordata:
            self.set_textures(floor)
            self.set_size(floor)
            self.set_objects(floor)
            self.render_scene(floor)

writing_variations = {
    'sku': ['SKU', 'product', 'article', 'skus'],
    'size': ['size', 'formaat', 'formaat (cm)'],
    'pattern': ['pattern', 'patroon', 'methode', 'legmethode', 'leg methode'],
    'grout': ['grout', 'voeg', 'groef', '2v', '4v', '2v/4v', 'voeg/groef', 'groef/voeg'],
    'suffix': ['suffix', 'toevoeging', 'bestandsnaam'],
    'scene': ['scene', 'set', 'lifestyle', 'life style', 'omgeving', 'kamer', 'room'],
    'laminate_regular': ['recht', 'normaal', 'gewoon', 'straight', 'regular'],
    'laminate_herringbone': ['visgraat', 'vis graat', 'visgraad', 'vis graad', 'herringbone', 'herring bone']
}