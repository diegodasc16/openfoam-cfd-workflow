import bpy  # Blender Python API
import csv  # To read parameters from a CSV file
import os   # For file and directory operations

# === RELATIVE PATHS ===
# Get the directory of the current Python script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build the full path to the CSV file that contains cylinder dimensions
csv_path = os.path.join(os.path.dirname(base_dir), "cyl_parameters.csv")

# Set the output directory where the generated STL files will be saved
output_dir = os.path.join(base_dir, "output")

# === CREATE OUTPUT FOLDER IF NOT EXISTS ===
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# === SET BLENDER UNIT SYSTEM TO METRIC WITH 1.0 SCALE ===
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0  # 1 Blender unit = 1 meter

# === USER OPTIONS ===
delete_existing_objects = True

# === CLEAN THE SCENE (Optional) ===
if delete_existing_objects:
    bpy.ops.object.select_all(action='SELECT')  # Select all objects
    bpy.ops.object.delete(use_global=False)     # Delete them

# === MAIN LOOP: CREATE CYLINDERS AND EXPORT TO STL ===
with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)  # Read CSV rows as dictionaries
    for i, row in enumerate(reader):  # Loop over each row
        try:
            # Read radius and height (assumed already in meters)
            radius = float(row['radius'])
            height = float(row['height'])

            # Add cylinder to the Blender scene
            bpy.ops.mesh.primitive_cylinder_add(
                radius=radius,
                depth=height,
                location=(0, 0, 0)
            )
            obj = bpy.context.object
            obj.name = f"Cylinder_{i+1}"

            # Export only this object to STL
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            export_path = os.path.join(output_dir, f"cylinder_{i+1}.stl")
            bpy.ops.export_mesh.stl(
                filepath=export_path,
                ascii=True,
                use_selection=True
            )
            print(f"✅ Exported: {export_path}")

            # Delete the object after exporting (optional cleanup)
            bpy.ops.object.delete()

        except Exception as e:
            print(f"⚠️ Error in row {i+1}: {e}")

