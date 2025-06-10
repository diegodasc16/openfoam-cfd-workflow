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
    control_dict_path = os.path.join(base_dir, 'templateCase/system/controlDict')
    decompose_dict_path = os.path.join(base_dir, 'templateCase/system/decomposeParDict')

    # Recupera solver dal controlDict
    if os.path.isfile(control_dict_path):
        with open(control_dict_path) as f:
            for line in f:
                if 'application' in line:
                    solver = line.split()[1].strip().strip(';')
                    break
            else:
                solver = 'simpleFoam'
    else:
        print("❌ controlDict not found. Defaulting to simpleFoam")
        solver = 'simpleFoam'

    # Recupera numero di processori
    if os.path.isfile(decompose_dict_path):
        with open(decompose_dict_path) as f:
            for line in f:
                if 'numberOfSubdomains' in line:
                    nproc = int(''.join(filter(str.isdigit, line)))
                    break
            else:
                nproc = 2
    else:
        nproc = 2

    run_parallel = input(f"⚙️  Run simulation in parallel with {nproc} processors? [y/N]: ").strip().lower() == 'y'

    print_section(f"Running solver: {solver}")

    for case_name in sorted(os.listdir(cases_dir)):
        case_path = os.path.join(cases_dir, case_name)
        if os.path.isdir(case_path) and case_name.startswith("case_"):
            print(f"\n➡️  Solving case: {case_name}")

            if run_parallel:
                run_command("decomposePar", case_path, "log_decomposePar_sim.txt")
                print("   ✅ decomposePar (simulation) completed")

                run_command(f"mpirun -np {nproc} {solver} -parallel", case_path, "log_sim_parallel.txt")
                print(f"   ✅ {solver} (parallel) completed")

                run_command("reconstructPar", case_path, "log_reconstruct_sim.txt")
                print("   ✅ reconstructPar completed")

                subprocess.run(f"find {case_path} -maxdepth 1 -type d -name 'processor*' -exec rm -rf {{}} +", shell=True)
            else:
                run_command(solver, case_path, "log_sim_serial.txt")
                print(f"   ✅ {solver} (serial) completed")

if __name__ == "__main__":
    main()
