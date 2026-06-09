import os
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def get_next_run_dir(base_dir="logs"):
    os.makedirs(base_dir, exist_ok=True)

    existing = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("run_")
    ]

    indices = []
    for d in existing:
        try:
            indices.append(int(d.split("_")[1]))
        except:
            pass

    next_index = max(indices, default=0) + 1
    run_dir = os.path.join(base_dir, f"run_{next_index:03d}")

    os.makedirs(run_dir)
    return run_dir

# SCENE_DIR = "/home/lburel/Sofa/plugins/BeamAdapter/examples"
# SCENE_DIR = "/home/lburel/Sofa/plugins/SofaPython3/examples"
# SCENE_DIR = "/home/lburel/Sofa/src/examples"

# SCENE_DIR = "/home/lburel/Sofa/src/examples/Benchmark"
# SCENE_DIR = "/home/lburel/Sofa/src/examples/Component"
# SCENE_DIR = "/home/lburel/Sofa/src/examples/Demos"
# SCENE_DIR = "/home/lburel/Sofa/src/examples/Objects"
# SCENE_DIR = "/home/lburel/Sofa/src/examples/Tutorials"
# SCENE_DIR = "/home/lburel/Sofa/src/examples/Validation"

SCENE_DIR = "/home/lucasbureltojo/~Sofa/src/examples"

# RUN_FEATURE = "/home/lburel/Sofa/plugins/SofaPython3/examples/LoaderScene_snapshot.py"
RUN_FEATURE = "/home/lucasbureltojo/~Sofa/plugins/SofaPython3/examples/LoaderScene_snapshot.py"
MAX_WORKERS = 16
TIMEOUT = 30
def find_scenes(root):
    scenes = []
    for r, _, files in os.walk(root):
        for f in files:
            if f.endswith(".py") or f.endswith(".scn"):
                scenes.append(os.path.join(r, f))
    return scenes

def safe_name(path):
    return path.replace("/", "_").replace(" ", "_")

def run_scene(scene, log_dir):
    start = time.time()
    cmd = ["python3", RUN_FEATURE, scene]

    log_file = os.path.join(log_dir, safe_name(scene) + ".log")

    python_trace = None

    # On ouvre le fichier log dès le début pour rediriger stdout/stderr
    with open(log_file, "wb") as f:
        # Entête du log
        f.write(b"=== CMD ===\n")
        f.write(" ".join(cmd).encode() + b"\n\n")
        f.flush()

        try:
            # Redirection directe vers le fichier log
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.STDOUT,
                timeout=TIMEOUT
            )
            code = result.returncode

        except subprocess.TimeoutExpired:
            code = -999
            python_trace = traceback.format_exc()

        except Exception:
            code = -998
            python_trace = traceback.format_exc()

        duration = time.time() - start

        # Footer du log
        f.write(b"\n=== RETURN CODE ===\n")
        f.write(str(code).encode() + b"\n\n")

        if python_trace:
            f.write(b"=== PYTHON TRACEBACK ===\n")
            f.write(python_trace.encode() + b"\n\n")

        f.write(b"=== DURATION ===\n")
        f.write(f"{duration:.2f} seconds\n".encode())

    # Détermination du statut
    if code == 0:
        status = "OK"
    elif code == -999:
        status = "TIMEOUT"
    elif code == -998:
        status = "PYTHON ERROR"
    elif code < 0:
        status = f"CRASH (signal {-code})"
    else:
        status = f"ERROR (code {code})"

    return scene, status, duration

def main():
    start_time = time.time()
    LOG_DIR = get_next_run_dir(base_dir="/home/lucasbureltojo/logs")
    print(f" Logs for this run: {os.path.abspath(LOG_DIR)}")
    scenes = find_scenes(SCENE_DIR)
    print(f"{len(scenes)} scenes found\n")

    results = []

    if MAX_WORKERS == 1:
        for scene in scenes:
            print("▶", scene)
            scene, status, duration = run_scene(scene, LOG_DIR)
            print("   ", status)
            results.append((scene, status))

    else:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(run_scene, s,LOG_DIR): s for s in scenes}

            for future in as_completed(futures):
                scene, status, duration = future.result()
                print(f"{status:20} | {scene}")
                results.append((scene, status))

    print("\n=== SUMMARY ===")

    stats = {}
    for _, status in results:
        stats[status] = stats.get(status, 0) + 1

    for k, v in stats.items():
        print(f"{k:20} : {v}")

    fails = [s for s, st in results if st != "OK"]

    if fails:
        print("\n FAILED SCENES:")
        for f in fails:
            print(" -", f)

    print(f"\n Logs saved in: {LOG_DIR}/")
    end_time = time.time()
    elapsed = end_time - start_time
    print("\n Total execution time: {:.2f} seconds".format(elapsed) )

if __name__ == "__main__":
    main()