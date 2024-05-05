import os, bpy
from PIL import Image, ImageStat

class Floordata():
    def __init__(self, sku, size, pattern, grout, suffix, texture_location, blendfile, lighting):
        self.sku = sku
        self.size_x, self.size_y = self.extract_size(size)
        self.pattern = pattern
        self.grout = grout
        self.suffix = suffix
        self.blendfile = blendfile
        self.min_light, self.max_light = self.extract_lighting(lighting)
        self.textures = self.collect_textures(texture_location)

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

    def collect_textures(self, texture_location):
        file_locations = []
        for file in os.listdir(texture_location):
            if self.sku in file:
                file_path = os.path.join(texture_location, file)
                file_locations.append(file_path)
                # print(f"Found texture: {file_path}")
        return file_locations

    def extract_lighting(self, lighting):
        delimiters = [', ', ',', '. ', '.', ' - ', ' -', '- ', '-', ' ']
        if lighting in writing_variations['empty']:
            return None, None
        else:
            for delimiter in delimiters:
                if delimiter in lighting:
                    split_lightning = lighting.split(delimiter)
                    return float(split_lightning[0]), float(split_lightning[1])
            print(f'Cant process lighting input: {lighting}, returning None')
            return None, None
    
class BlenderFloorProcessor:
    def __init__(self, texture_location, output_location, blend_filename):
        self.camera_name = 'MAIN_CAMERA'
        self.texture_location = texture_location
        self.output_location = output_location
        self.blend_filename = blend_filename

    def set_pattern(self, floor):
        obj_regular = 'FLOOR_STANDARD'
        obj_herringbone = 'FLOOR_HERRINGBONE'
        floor_mat = 'FLOOR_MATERIAL'
        if floor.pattern in writing_variations['laminate_regular'] or '':
            return obj_regular, floor_mat
        elif floor.pattern in writing_variations['laminate_herringbone']:
            return obj_herringbone, floor_mat
        else:
            print(f'PATTERN FOR {floor.sku} NOT RECOGNIZED')

    def set_textures(self, floor):
        object_name, material_name = self.set_pattern(floor)
        mat = bpy.data.materials[material_name]
        nodes = mat.node_tree.nodes

        # Define the specific order of node names
        node_names = [
            "Image Texture.001", 
            "Image Texture.002", 
            "Image Texture.003", 
            "Image Texture.004", 
            "Image Texture.005", 
            "Image Texture.006", 
            "Image Texture.007", 
            "Image Texture.008"
        ]

        # Ensure there are enough textures to match the nodes
        if len(floor.textures) > len(node_names):
            print(f"{floor.sku} contains {len(floor.textures)} textures, skipping {len(floor.textures)-8} texture(s)")
            floor.textures = floor.textures[:len(node_names)]

        # Loop over filenames and corresponding node names
        for filename, node_name in zip(floor.textures, node_names):
            image_path = os.path.join(self.texture_location, filename)
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
        if len(floor.textures) > 0 and len(multi_texture_node.outputs) >= len(floor.textures):
            link = mat.node_tree.links.new
            link(multi_texture_node.outputs[len(floor.textures) - 1], reroute_node.inputs[0])
        else:
            print("Not enough outputs in MultiTexture node or no textures specified.")

    def set_planks(self, floor):
        object_name, material_name = self.set_pattern(floor)
        obj = bpy.data.objects.get(object_name)
        print(f'SETTINGS FOR {floor.sku}, PATTERN: {floor.pattern}, GROUT: {floor.grout}')
        if obj and 'GeometryNodes' in obj.modifiers:
            if object_name == 'FLOOR_STANDARD':
                modifier = obj.modifiers["GeometryNodes"]
                modifier["Input_2"] = modifier["Socket_0"] = float(floor.size_x) / 100
                modifier["Input_3"] = modifier["Socket_3"] = float(floor.size_y) / 100
                if floor.grout in writing_variations['2v']:
                    modifier["Input_5"] = float(0) # along the short side
                    modifier["Input_6"] = 0.0005 # along the tall side
                elif floor.grout in writing_variations['4v']:
                    modifier["Input_5"] = modifier["Input_6"] = 0.0005 # along both sides
                else:
                    modifier["Input_5"] = modifier["Input_6"] = float(0) # along both sides
            elif object_name == 'FLOOR_HERRINGBONE':
                modifier = obj.modifiers["GeometryNodes"]
                modifier["Input_2"] = float(floor.size_x) / 100
                modifier["Input_3"] = float(floor.size_y) / 100
                if floor.grout in writing_variations['4v']:
                    modifier["Input_5"] = 0.0005
                else:
                    modifier["Input_5"] = float(0) # along both sides
        else:
            print(f"Object '{object_name}' not found or it doesn't have a 'GeometryNodes' modifier.")

    def set_objects(self, floor):
        regular_obj = bpy.data.objects.get('FLOOR_STANDARD')
        herringbone_obj = bpy.data.objects.get('FLOOR_HERRINGBONE')
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

    def calculate_brightness(self, floor):
        if floor.min_light == None:
            return None
        else:
            image_path = floor.textures[0]
            img = Image.open(image_path).convert('L')  # Convert to grayscale
            stat = ImageStat.Stat(img)
            brightness = stat.mean[0]  # Average brightness

            # Map brightness to light strength
            normalized_brightness = brightness / 255
            light_strength = floor.max_light - normalized_brightness * (floor.max_light - floor.min_light)
            return light_strength

    def set_light(self, floor, light_strength): # Update the light strength in Blender
        if light_strength == None:
            print(f'NO LIGHTING SETTINGS FOR {floor.sku}, USING DEFAULT VALUES')
        else:
            light_object = bpy.data.objects.get('MAIN_LIGHT')
            if light_object and light_object.type == 'LIGHT':
                light_object.data.energy = light_strength
                print(f"Set MAIN_LIGHT strength to {light_strength}")
            else:
                print("MAIN_LIGHT not found or is not a light object.")

    def render_scene(self, floor):
        self.set_camera()
        full_output_path = os.path.join(self.output_location, floor.sku + floor.suffix)
        print(f'Rendering {floor.sku}')
        bpy.context.scene.render.filepath = full_output_path
        bpy.ops.render.render(write_still=True)

    def batch_process(self, render_floordata):
        total_images = 0
        for i in render_floordata:
            if i.blendfile == self.blend_filename:
                total_images += 1
        images_rendered = 0

        for floor in render_floordata:
            if floor.blendfile == self.blend_filename:
                self.set_textures(floor)
                self.set_planks(floor)
                self.set_objects(floor)
                light_strength = self.calculate_brightness(floor)
                self.set_light(floor, light_strength)
                self.render_scene(floor)
                images_rendered += 1
                print(f'\nPROGRESS: {(images_rendered/total_images)*100}%\n')
            else:
                print(f'Skipping {floor.sku} because it belongs to: {floor.blendfile}.')

writing_variations = {
    'sku': ['SKU', 'product', 'article', 'skus'],
    'size': ['size', 'formaat', 'formaat (cm)'],
    'pattern': ['pattern', 'patroon', 'methode', 'legmethode', 'leg methode'],
    'grout': ['grout', 'voeg', 'groef', '2v', '4v', '2v/4v', 'voeg/groef', 'groef/voeg'],
    'suffix': ['suffix', 'toevoeging', 'bestandsnaam'],
    'blendfile': ['blendfile', 'blend', 'blender', 'file', 'bestand', 'bestandsnaam', 'filename', 'file name', '.blend'],
    'lighting': ['lighting', 'belichting', 'light', 'lightning', 'licht'],
    'laminate_regular': ['recht', 'normaal', 'gewoon', 'straight', 'regular'],
    'laminate_herringbone': ['visgraat', 'vis graat', 'visgraad', 'vis graad', 'herringbone', 'herring bone'],
    '0v': ['0v', '0 v', '0', '', 'nvt', 'n.v.t.', '-', 'geen'],
    '2v': ['2v', '2 v', '2', 'lange zijde', 'length', 'lengte' ],
    '4v': ['4v', '4 v', '4', 'beide', 'rondom' ],
    'empty': ['', ' ', 'nvt', 'n.v.t.', '-', 'None', None]
}