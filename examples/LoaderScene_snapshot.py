import Sofa
import SofaRuntime
import Sofa.Simulation
import importlib.util
import sys
import os

def load_scene_module(scene_path): #Function to load a scene from a path (.py)
    module_name = os.path.splitext(os.path.basename(scene_path))[0]

    spec = importlib.util.spec_from_file_location(module_name, scene_path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load Python module: {scene_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module

def run_loaded_scene(root):
    Sofa.Simulation.initRoot(root)

    print("Initial time is = " + str(root.time.value))

    snapshot = Sofa.Core.Snapshot_Python()

    Sofa.Simulation.animate(root, root.dt.value)
    print("After first animate, time is = " + str(root.time.value))

    print("Save a snapshot")
    root.executeSaveSnapshotVisitor(snapshot)
    print("=======> save done")

    Sofa.Simulation.animate(root, root.dt.value)
    print("After second animate, time is = " + str(root.time.value))

    print("Load a snapshot")
    root.executeLoadSnapshotVisitor(snapshot, snapshot.getNumberOfSnapshot() - 1)
    print("=======> load done")

    print("After load, time is = " + str(root.time.value))

    Sofa.Simulation.animate(root, root.dt.value)
    print("After final animate, time is = " + str(root.time.value))

    print("Simulation done")

def run_scn_scene(scene_file):
    SofaRuntime.importPlugin("Sofa.Component.StateContainer")

    scene_file = os.path.abspath(scene_file)

    if not os.path.isfile(scene_file):
        raise FileNotFoundError(f"Scene file not found: {scene_file}")


    print("Loading .scn scene in Python:")
    print(scene_file)

    root = Sofa.Simulation.load(scene_file)

    # if root is None:
    #     raise RuntimeError(f"Cannot load scene: {scene_file}")

    run_loaded_scene(root)

def main(scene_file):
    import SofaRuntime
    import Sofa.Gui

    ext = os.path.splitext(scene_file)[1]

    if ext == ".py" :

        SofaRuntime.importPlugin("Sofa.Component.StateContainer")
        SofaRuntime.importPlugin("SofaImGui")

        scene_module = load_scene_module(scene_file)

        root = Sofa.Core.Node("root")

        scene_module.createScene(root)

        Sofa.Simulation.initRoot(root)

        print("time is = "+ str(root.time.value))
        Sofa.Simulation.animate(root, root.dt.value)

        snapshot = Sofa.Core.Snapshot_Python()
        print("Save a snapshot")
        root.executeSaveSnapshotVisitor(snapshot)
        print("=======>save done")

        print("time is = "+ str(root.time.value))
        Sofa.Simulation.animate(root, root.dt.value)
        print("time is = "+ str(root.time.value))
        print("Load a snapshot")
        root.executeLoadSnapshotVisitor(snapshot,0)
        print("=======>load done")

        print("time is = "+ str(root.time.value))

        print("Simulation done")

    elif ext ==".scn":
        print(scene_file)
        run_scn_scene(scene_file)

    elif ext ==".xml":
        print(scene_file)
        run_scn_scene(scene_file)


    else:
        print("Unsupported file")



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("no file")
    else:
        scene_path = sys.argv[1]
        main(scene_path)