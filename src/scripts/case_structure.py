import os
import shutil

# === BASE PATHS ===
# Get the absolute path of the current script file.
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go one level up in directory hierarchy to locate the source directory 
# (e.g., where "templateCase" is stored).
src_dir = os.path.dirname(current_dir)

# Path to the base OpenFOAM case template 
# (used as a blueprint for each generated case)
template_case = os.path.join(src_dir, "templateCase")

# Folder containing all STL geometry files that we want to simulate
stl_folder = os.path.join(current_dir, "output")

# Where all new OpenFOAM cases will be created (one per STL file)
cases_dir = os.path.join(src_dir, "cases")

# Paths to mesh configuration templates (snappyHexMeshDict and surfaceFeatureExtractDict)
template_snappy = os.path.join(src_dir, "mesh", "snappyHexMeshDict")
template_surface = os.path.join(src_dir, "mesh", "surfaceFeatureExtractDict")


# === Ensure output folders exist ===
# Create the directory for generated cases if it doesn't already exist
os.makedirs(cases_dir, exist_ok=True)

# === Read template files once ===
# Read the contents of snappyHexMeshDict template into memory
with open(template_snappy, "r") as f:
    snappy_template = f.read()

# Read the contents of surfaceFeatureExtractDict template into memory
with open(template_surface, "r") as f:
    surface_template = f.read()

# === Process each STL ===
# Iterate through all files in the STL folder. Each STL file represents a different cylinder.
for i, filename in enumerate(os.listdir(stl_folder), start=1):

    # Only process files ending with ".stl" (case-insensitive)
    if filename.lower().endswith(".stl"):

        # Create a unique case name (e.g., case_1, case_2, ...)
        case_name = f"case_{i}"
        case_path = os.path.join(cases_dir, case_name)

        # Step 1: Copy the entire template case folder into the new case folder.
        # This sets up the base OpenFOAM directory structure and files.
        shutil.copytree(template_case, case_path, dirs_exist_ok=True)

        # Step 2: Copy the STL file into the case's triSurface folder
        # This is where OpenFOAM expects geometry files for meshing.
        trisurf_path = os.path.join(case_path, "constant", "triSurface")
        os.makedirs(trisurf_path, exist_ok=True)
        stl_src = os.path.join(stl_folder, filename)
        stl_dst = os.path.join(trisurf_path, filename)
        shutil.copy(stl_src, stl_dst)

        # Step 3: Customize mesh-related dictionaries with the specific STL file name
        # Replace placeholder values (like "cylinder.stl") in the template with the actual file name
        emesh_name = filename.replace(".stl", ".eMesh")  # Expected mesh feature file
        snappy_dict = snappy_template.replace("cylinder.stl", filename)
        snappy_dict = snappy_dict.replace("cylinder.eMesh", emesh_name)
        surface_dict = surface_template.replace("cylinder.stl", filename)

        # Step 4: Write the updated configuration files into the new case's system folder
        system_dir = os.path.join(case_path, "system")
        with open(os.path.join(system_dir, "snappyHexMeshDict"), "w") as f:
            f.write(snappy_dict)
        with open(os.path.join(system_dir, "surfaceFeatureExtractDict"), "w") as f:
            f.write(surface_dict)

        # Log progress to the console

        print(f"✅ Generated {case_name} with {filename}")

