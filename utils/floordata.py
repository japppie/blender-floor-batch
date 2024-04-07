import os

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
                print(f"Found texture: {file}")
        return int(texture_count)