__author__ = 'Patrick Rainsberry'

import adsk.core
import adsk.fusion
import traceback


# Externally usable function to get all relevant application objects easily in a dictionary
def get_app_objects():

    app = adsk.core.Application.cast(adsk.core.Application.get())

    # Get import manager
    import_manager = app.importManager

    # Get User Interface
    ui = app.userInterface

    # Get active design
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    document = app.activeDocument

    # Get Design specific elements
    units_manager = design.unitsManager
    export_manager = design.exportManager
    root_comp = design.rootComponent
    time_line = product.timeline

    # Get top level collections
    all_occurrences = root_comp.allOccurrences
    all_components = design.allComponents

    app_objects = {
        'app': app,
        'design': design,
        'import_manager': import_manager,
        'ui': ui,
        'units_manager': units_manager,
        'all_occurrences': all_occurrences,
        'all_components': all_components,
        'root_comp': root_comp,
        'time_line': time_line,
        'export_manager': export_manager,
        'document': document
    }
    return app_objects


def start_group():
    """
    Starts a time line group

    :return: The index of the time line
    :rtype: int
    """
    # Gets necessary application objects
    app_objects = get_app_objects()

    # Start time line group
    start_index = app_objects['time_line'].markerPosition

    return start_index


def end_group(start_index):
    """
    Ends a time line group

    :param start_index: Time line index
    :type start_index: int
    :return:
    :rtype:
    """

    # Gets necessary application objects
    app_objects = get_app_objects()

    end_index = app_objects['time_line'].markerPosition - 1

    app_objects['time_line'].timelineGroups.add(start_index, end_index)


def import_dxf(dxf_file, component, plane) -> adsk.core.ObjectCollection:
    """
    Import dxf file with one sketch per layer.

    :param dxf_file: The full path to the dxf file
    :type dxf_file: str
    :param component: The target component for the new sketch(es)
    :type component: adsk.fusion.Component
    :param plane: The plane on which to import the DXF file.
    :type plane: adsk.fusion.ConstructionPlane or adsk.fusion.BRepFace
    :return: A Collection of the created sketches
    :rtype: adsk.core.ObjectCollection
    """
    import_manager = get_app_objects()['import_manager']
    dxf_options = import_manager.createDXF2DImportOptions(dxf_file, plane)
    import_manager.importToTarget(dxf_options, component)
    sketches = dxf_options.results
    return sketches


def sketch_by_name(sketches, name):
    """
    Finds a sketch by name in a list of sketches

    Useful for parsing a collection of  sketches such as DXF import results.

    :param sketches: A list of sketches.
    :type sketches: adsk.fusion.Sketches
    :param name: The name of the sketch to find.
    :return: The sketch matching the name if it is found.
    :rtype: adsk.fusion.Sketch
    """
    return_sketch = None
    for sketch in sketches:
        if sketch.name == name:
            return_sketch = sketch
    return return_sketch


def extrude_all_profiles(sketch, distance, component, operation) -> adsk.fusion.ExtrudeFeature:
    """
    Create extrude features of all profiles in a sketch

    The new feature will be created in the given target component and extruded by a distance

    :param sketch: The sketch from which to get profiles
    :type sketch: adsk.fusion.Sketch
    :param distance: The distance to extrude the profiles.
    :type distance: float
    :param component: The target component for the extrude feature
    :type component: adsk.fusion.Component
    :param operation: The feature operation type from enumerator.  
    :type operation: adsk.fusion.FeatureOperations
    :return: THe new extrude feature.
    :rtype: adsk.fusion.ExtrudeFeature
    """
    profile_collection = adsk.core.ObjectCollection.create()
    for profile in sketch.profiles:
        profile_collection.add(profile)

    extrudes = component.features.extrudeFeatures
    ext_input = extrudes.createInput(profile_collection, operation)
    distance_input = adsk.core.ValueInput.createByReal(distance)
    ext_input.setDistanceExtent(False, distance_input)
    extrude_feature = extrudes.add(ext_input)
    return extrude_feature


def create_component(target_component, name) -> adsk.fusion.Occurrence:
    """
    Creates a new empty component in the target component

    :param target_component: The target component for the new component
    :type target_component:
    :param name: The name of the new component
    :type name: str
    :return: The reference to the occurrence of the newly created component.
    :rtype: adsk.fusion.Occurrence
    """
    transform = adsk.core.Matrix3D.create()
    new_occurrence = target_component.occurrences.addNewComponent(transform)
    new_occurrence.component.name = name
    return new_occurrence

