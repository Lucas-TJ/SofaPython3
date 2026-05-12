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
SCENE_DIR = "/home/lburel/Sofa/plugins/SofaPython3/examples"
# SCENE_DIR = "/home/lburel/Sofa/src/examples"
RUN_FEATURE = "/home/lburel/Sofa/plugins/SofaPython3/examples/LoaderScene_snapshot.py"
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
    cmd = ["python3",RUN_FEATURE, scene]

    log_file = os.path.join(log_dir, safe_name(scene) + ".log")

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT
        )

        stdout = result.stdout
        stderr = result.stderr
        code = result.returncode

        python_trace = None

    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or b""
        stderr = e.stderr or b""
        code = -999
        python_trace = traceback.format_exc()

    except Exception as e:
        stdout = b""
        stderr = str(e).encode()
        code = -998
        python_trace = traceback.format_exc()

    duration = time.time() - start
    # write the log after crash
    with open(log_file, "wb") as f:
        f.write(b"=== CMD ===\n")
        f.write(" ".join(cmd).encode() + b"\n\n")

        f.write(b"=== RETURN CODE ===\n")
        f.write(str(code).encode() + b"\n\n")

        f.write(b"=== STDOUT ===\n")
        f.write(stdout + b"\n\n")

        f.write(b"=== STDERR ===\n")
        f.write(stderr + b"\n")

        if python_trace:
            f.write(b"=== PYTHON TRACEBACK ===\n")
            f.write(python_trace.encode() + b"\n")

        f.write(b"=== DURATION ===\n")
        f.write(f"{duration:.2f} seconds\n\n".encode())

    # status
    if code == 0:
        status = "OK"
    elif code < 0:
        status = f"CRASH (signal {-code})"
    else:
        status = f"ERROR (code {code})"

    return scene, status, duration

def main():
    start_time = time.time()
    LOG_DIR = get_next_run_dir(base_dir="/home/lburel/logs")
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