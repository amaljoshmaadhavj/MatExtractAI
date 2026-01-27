def cross_check_microstructure_processing(micro, processing_routes):
    """
    Logical consistency checks between microstructure and processing.
    Only apply rules when material form matches.
    """
    issues = []

    material_form = micro.get("material_form")

    # Only flag equi-axed grains for EXTRUDED material
    if (
        material_form == "extruded profile"
        and micro.get("grain_morphology") == "equi-axed"
    ):
        issues.append("Equi-axed grains uncommon for extruded material")

    return issues
