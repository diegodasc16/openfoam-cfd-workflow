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
    template_dict = os.path.join(base_dir, 'templateCase/system/decomposeParDict')
    cases_dir = os.path.join(base_dir, 'cases')

    # Determina numero di processori
    if os.path.isfile(template_dict):
        with open(template_dict) as f:
            for line in f:
                if 'numberOfSubdomains' in line:
                    nproc = int(''.join(filter(str.isdigit, line)))
                    break
            else:
                nproc = 2
    else:
        print("❌ decomposeParDict not found. Using 2 processors by default.")
        nproc = 2

    run_parallel = input(f"⚙️  Run snappyHexMesh in parallel with {nproc} processors? [y/N]: ").strip().lower() == 'y'

    print_section("Running snappyHexMesh")

    for case_name in sorted(os.listdir(cases_dir)):
        case_path = os.path.join(cases_dir, case_name)
        if os.path.isdir(case_path) and case_name.startswith("case_"):
            print(f"\n➡️  Processing: {case_name}")

            if run_parallel:
                run_command("decomposePar", case_path, "log_decomposePar.txt")
                print("   ✅ decomposePar completed")

                run_command(f"mpirun -np {nproc} snappyHexMesh -parallel", case_path, "log_snappyHex.txt")
                print(f"   ✅ snappyHexMesh (parallel, {nproc} procs) completed")

                run_command("reconstructParMesh -latestTime", case_path, "log_reconstructParMesh.txt")
                print("   ✅ reconstructParMesh completed")
            else:
                run_command("snappyHexMesh", case_path, "log_snappyHex_serial.txt")
                print("   ✅ snappyHexMesh (serial) completed")

            # Sostituisce constant/polyMesh con il più recente
            time_dirs = [d for d in os.listdir(case_path) if d.replace('.', '', 1).isdigit() and d != '0']
            latest_time = sorted(time_dirs, key=lambda x: float(x))[-1] if time_dirs else None

            if not latest_time:
                print(f"⚠️  No valid mesh folder found in: {case_name}")
                continue

            src_poly = os.path.join(case_path, latest_time, 'polyMesh')
            dst_poly = os.path.join(case_path, 'constant', 'polyMesh')

            if os.path.isdir(src_poly):
                print(f"   🔁 Replacing constant/polyMesh with {latest_time}/polyMesh")
                subprocess.run(f"rm -rf {dst_poly}", shell=True)
                subprocess.run(f"cp -r {src_poly} {dst_poly}", shell=True)
                print("   ✅ Replacement completed")
            else:
                print(f"❌ polyMesh not found in {latest_time}/")

            # Crea .foam file
            foam_file = os.path.join(case_path, f"{case_name}.foam")
            open(foam_file, 'a').close()
            print(f"   📁 Created {case_name}.foam")

            # Rimuove directory processor* e time directory
            subprocess.run(f"find {case_path} -maxdepth 1 -type d -name 'processor*' -exec rm -rf {{}} +", shell=True)
            if latest_time and latest_time != '0':
                subprocess.run(f"rm -rf {os.path.join(case_path, latest_time)}", shell=True)

if __name__ == "__main__":
    main()
