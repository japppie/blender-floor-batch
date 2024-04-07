import os, bpy

class Floordata():
    def __init__(self, sku, size, pattern, grout, suffix, image_location):
        self.sku = sku
        self.size_x, self.size_y = self.extract_size(size)
        self.pattern = pattern
        self.grout = grout
        self.suffix = suffix
        self.filenames = []
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
    def __init__(self, camera_name, object_name, material_name, image_location, output_location):
        self.camera_name = camera_name
        self.object_name = object_name
        self.material_name = material_name
        self.mat = bpy.data.materials[material_name]
        self.nodes = self.mat.node_tree.nodes
        self.image_location = image_location
        self.output_location = output_location

    def set_textures(self, floor):
        for i, filename in enumerate(floor.filenames):
            node_name = f'tex{i:02}'
            image_path = os.path.join(self.image_location, filename)

            node = self.nodes.get(node_name)
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

    def set_size(self, floor):
        obj = bpy.data.objects.get(self.object_name)
        if obj and 'GeometryNodes' in obj.modifiers:
            modifier = obj.modifiers["GeometryNodes"]
            modifier["Input_2"] = floor.size_x / 100
            modifier["Socket_0"] = floor.size_x / 100
            modifier["Input_3"] = floor.size_y / 100
            modifier["Socket_3"] = floor.size_y / 100
        else:
            print(f"Object '{self.object_name}' not found or it doesn't have a 'GeometryNodes' modifier.")

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
            self.render_scene(floor)

CSVvariations = {
    'sku': ['SKU', 'product', 'article', 'skus'],
    'size': ['size', 'formaat', 'formaat (cm)'],
    'pattern': ['pattern', 'patroon', 'methode', 'legmethode', 'leg methode'],
    'grout': ['grout', 'voeg', 'groef', '2v', '4v', '2v/4v', 'voeg/groef', 'groef/voeg'],
    'suffix': ['suffix', 'toevoeging', 'bestandsnaam']
}