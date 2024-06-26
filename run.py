# TODO: Specify the location of the local Git repo:
github_repo_location = r'C:\Users\Jasper\Documents\GitHub\blender-floor-batch'

import bpy, csv, os, sys, importlib
from PIL import Image, ImageStat
sys.path.append(github_repo_location)
import utils.floordata
from utils.floordata import Floordata, BlenderFloorProcessor, writing_variations

def fix_directory(directory):
    directory = directory.replace('\\', '/')
    if directory[-1] != '/':
        directory += '/'
    return directory

github_repo_location = fix_directory(github_repo_location)

# DECLARE VARIABLES
texture_location = github_repo_location + 'textures/'
output_location = github_repo_location + 'output/'
csv_location = github_repo_location + 'assets/demo_floors.csv'

# CHECK DIRECTORIES
if not os.path.exists(github_repo_location) or not os.path.isdir(github_repo_location):
    raise ValueError("Invalid GitHub repo location")

if not os.path.exists(csv_location) or not os.path.isfile(csv_location):
    raise ValueError("Invalid CSV file location")

if not os.path.exists(texture_location) or not os.path.isdir(texture_location):
    raise ValueError("Invalid texture location")

if not os.path.exists(output_location) or not os.path.isdir(output_location):
    raise ValueError("Invalid output location")

def get_blend_filename():
    return os.path.basename(bpy.data.filepath)

blend_filename = get_blend_filename()
print(f'\nOnly rendering floors belonging to: {blend_filename}\n')

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
            blendfile = row[column_names['blendfile']]
            if 'lighting' in column_names:
                lighting = row[column_names['lighting']]
            else:
                lighting = None
            # Dynamically reload the floordata module before creating Floordata objects
            importlib.reload(utils.floordata)
            floor_data = Floordata(sku, size, pattern, grout, suffix, texture_location, blendfile, lighting)
            floordata_list.append(floor_data)

    for i in floordata_list:
        if len(i.textures) == 0:
            missing_floordata.append(i.sku)
        else:
            render_floordata.append(i)



# Initiate Blender
processor = BlenderFloorProcessor(texture_location, output_location, blend_filename)

# Start batch render process
processor.batch_process(render_floordata)

# Print missing textures
print("\n###############################################")
print("###  Couldn't find the following textures:  ###")
print("###############################################")
print(missing_floordata, '\n\n')