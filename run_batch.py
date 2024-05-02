# TODO: Specify the location of the local Git repo:
github_repo_location = '/Users/gebruiker/Documents/GitHub/blender-floor-batch/'

import bpy, csv, os, sys
from collections import defaultdict
sys.path.append(github_repo_location)
from utils.floordata import Floordata, BlenderFloorProcessor, writing_variations

def fix_directory(directory):
    directory = directory.replace('\\', '/')
    if directory[-1] != '/':
        directory += '/'
    return directory

github_repo_location = fix_directory(github_repo_location)

# DECLARE VARIABLES
camera_name = 'MAIN_CAMERA'
texture_location = github_repo_location + 'textures/'
output_location = github_repo_location + 'output/'
csv_location = github_repo_location + 'assets/demo_floors.csv'

def group_by_scene(floordata_list):
    scene_dict = defaultdict(list)
    for data in floordata_list:
        scene_dict[data.scene].append(data)
    return scene_dict

def detect_column_names(header, writing_variations):
    detected_names = {}
    for standard_name, variations in writing_variations.items():
        for variation in variations:
            if variation in header:
                detected_names[standard_name] = variation
                break
    return detected_names

floordata_list = []
render_floordata = []
missing_floordata = []
with open(csv_location) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    header = csv_reader.fieldnames
    column_names = detect_column_names(header, writing_variations)
    for row in csv_reader:
        sku = row[column_names['sku']]
        if sku == '':
            continue        
        else:            
            size = row[column_names['size']]
            pattern = row[column_names['pattern']]
            grout = row[column_names['grout']]
            suffix = row[column_names['suffix']]
            scene = row[column_names['scene']]
            floor_data = Floordata(sku, size, pattern, grout, suffix, texture_location, scene)
            floordata_list.append(floor_data)

    for i in floordata_list:
        if i.texture_count == 0:
            missing_floordata.append(i.sku)
        else:
            render_floordata.append(i)

# Group the render_floordata by their scene
scene_groups = group_by_scene(render_floordata)

# Processing each scene batch
for scene_file, floordata_batch in scene_groups.items():
    scene_path = os.path.join(github_repo_location, 'assets/', scene_file)
    # Load the blend file corresponding to the current scene
    bpy.ops.wm.open_mainfile(filepath=scene_path)

    # Create an instance of the processor if not already created
    processor = BlenderFloorProcessor(camera_name, texture_location, output_location)

    # Process the batch of floor data for the current scene
    processor.batch_process(floordata_batch)
    print(f"Completed processing for scene: {scene_file}")

# Print missing textures
print("\n###############################################")
print("###  Couldn't find the following textures:  ###")
print("###############################################")
print(missing_floordata)