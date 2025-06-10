import os
import subprocess
import sys

def print_section(title):
    print("\n" + "="*60)
    print(f"\U0001F537 {title}")
    print("="*60)

def run_command(command, cwd, log_file):
    log_path = os.path.join(cwd, log_file)
    with open(log_path, 'w') as log:
        result = subprocess.run(command, cwd=cwd, shell=True, stdout=log, stderr=log)
    if result.returncode != 0:
        print(f"❌ Error while running '{command}' in {os.path.basename(cwd)} (see {log_file})")
        sys.exit(1)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    cases_dir = os.path.join(base_dir, 'cases')

    print_section("Preprocessing cases: blockMesh and surfaceFeatureExtract")

    for case_name in sorted(os.listdir(cases_dir)):
        case_path = os.path.join(cases_dir, case_name)
        if os.path.isdir(case_path) and case_name.startswith("case_"):
            print(f"\n➡️  Processing: {case_name}")

            run_command("blockMesh", case_path, "log_blockMesh.txt")
            print("   ✅ blockMesh completed")

            run_command("surfaceFeatureExtract", case_path, "log_surfaceFeatures.txt")
            print("   ✅ surfaceFeatureExtract completed")

if __name__ == "__main__":
    main()
