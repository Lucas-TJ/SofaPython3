import Sofa

def main():
    # Make sure to load all necessary libraries
    import SofaRuntime
    # import Sofa.Gui

    SofaRuntime.importPlugin("Sofa.Component.StateContainer")
    # SofaRuntime.importPlugin("SofaImGui")

    # Call the above function to create the scene graph
    root = Sofa.Core.Node("root")
    createScene(root)

    # Once defined, initialization of the scene graph
    Sofa.Simulation.initRoot(root)

    # # Use GUI
    # Sofa.Gui.GUIManager.Init("myscene", "imgui")
    # Sofa.Gui.GUIManager.createGUI(root, __file__)
    # Sofa.Gui.GUIManager.SetDimension(1080, 800)
    #
    # Sofa.Gui.GUIManager.MainLoop(root)
    # Sofa.Gui.GUIManager.closeGUI()

    # print("The simulation is done but...")
    # print("time is = "+ str(root.time.value))

    # Create a snapshot container (list of string)
    snapshot_container = []

    snapshot = Sofa.Core.Snapshot_Python()

    # for iteration in range(5):
    #     print(f'Iteration #{iteration}')
    #     Sofa.Simulation.animate(root, root.dt.value)
    #     snapshot_string = root.executeSaveSnapshotVisitor(snapshot)
    #     # print("Snapshot n°",iteration)
    #     # print(snapshot_string)
    #     snapshot_container.append(snapshot_string)
    # print("Simulation made 10 time steps. Done")

    print("time is = "+ str(root.time.value))
    Sofa.Simulation.animate(root, root.dt.value)

    print("Save a snapshot")
    snapshot_string = root.executeSaveSnapshotVisitor(snapshot)
    print("save done")

    print("time is = "+ str(root.time.value))
    Sofa.Simulation.animate(root, root.dt.value)
    print("time is = "+ str(root.time.value))
    print("Load a snapshot")
    root.executeLoadSnapshotVisitor(snapshot,0)
    print("load done")

    print("time is = "+ str(root.time.value))


# Function called when the scene graph is being created
def createScene(root):
    root.gravity=[0, 0, 0]
    root.dt=0.1

    root.addObject("RequiredPlugin", pluginName=[   'Sofa.Component.Collision.Geometry',
                                                    'Sofa.Component.Constraint.Projective',
                                                    'Sofa.Component.LinearSolver.Iterative',
                                                    'Sofa.Component.Mass',
                                                    'Sofa.Component.ODESolver.Backward',
                                                    'Sofa.Component.SolidMechanics.Spring',
                                                    'Sofa.Component.StateContainer',
                                                    'Sofa.Component.Visual'
                                                    ])
    root.addObject('DefaultAnimationLoop')
    root.addObject('VisualStyle', displayFlags="showBehavior showCollisionModels")

    root.addObject('EulerImplicitSolver', name="EulerImplicit", rayleighStiffness="0.1", rayleighMass="0.1" )
    root.addObject('CGLinearSolver', name="CGSolver", iterations="25", tolerance="1e-5", threshold="1e-5")
    root.addObject('InteractiveCamera')
    root.addObject('MechanicalObject', name="Particles", template="Vec3",
                   position="0 0 0 0 0 1",
                   velocity="0 0 0 0 1 0")
    root.addObject('UniformMass', name="Mass", totalMass="1")
    root.addObject('FixedProjectiveConstraint', indices="0")
    root.addObject('SpringForceField', name="Springs", stiffness="100", damping="1", spring="0 1 10 1 1")
    root.addObject('SphereCollisionModel', radius="0.1")

    return root


# Function used only if this script is called from a python environment
if __name__ == '__main__':
    main()
