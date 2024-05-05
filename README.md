For use in a single Blendfile, import the contents from run.py into the Blender python editor. Make sure to update the path in row 2.

Batch Processor not yet working


# Short description
Set up a render queue for multiple floors in Blender
Using Blender 4.1 and Floor Generator 2.0 by NodeCrafted https://blendermarket.com/products/floor-generator (you require a license to use the file, go buy it at Blender Market. The use of this script is free.)

Script imports CSV
Writes all floor data into instance of Floordata class
Changes all textures, tile sizes and patterns in the floor generator
Dynamically changes light strength based on texture brightness
Renders 'MAIN_CAMERA'

# BEFORE YOU RUN THIS SCRIPT
- Render camera should be called 'MAIN_CAMERA'
- Don't change any names/labels in the Geo nodes and materialnodes setup

# TO DO
Possibly create separate settings file
Fix batch solution