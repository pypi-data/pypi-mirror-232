if __name__ == '__main__':
    import pathlib
    import json

    from ladybug_radiance.study.radiation import RadiationStudy
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug_radiance.skymatrix import SkyMatrix
    from ladybug_geometry.geometry3d import Mesh3D

    def evaluate_boolean(value):
        if value == 'true' or value == 'True' or value is True:
            return True
        else:
            return False

    # map function inputs to script
    north = {{self.north}}
    high_sky_density = evaluate_boolean('{{self.high_sky_density}}')
    ground_reflectance = {{self.ground_reflectance}}
    avg_irr = evaluate_boolean('{{self.average_irradiance}}')
    use_benefit = evaluate_boolean('{{self.radiation_benefit}}')
    bal_temp = {{self.balance_temp}}
    offset_distance = {{self.offset_dist}}
    run_period = AnalysisPeriod.from_string('{{self.run_period}}')
    display_context = evaluate_boolean('{{self.display_context}}')

    # load geometry
    context_file = pathlib.Path('context_geo.json')
    geometry_file = pathlib.Path('input_geo.json')

    input_geo = json.loads(geometry_file.read_text())
    study_mesh = Mesh3D.from_dict(input_geo)

    context_geo = []
    if context_file.is_file():
        context_data = json.loads(context_file.read_text())
        context_geo = [Mesh3D.from_dict(context_data)]

    # compute sky matrix
    hoys = None if len(run_period) == 8760 else run_period.hoys
    if use_benefit:
        sky_matrix = SkyMatrix.from_epw_benefit(
            'weather.epw', bal_temp, 2, hoys,
            north, high_sky_density, ground_reflectance
        )
    else:
        sky_matrix = SkyMatrix.from_epw(
            'weather.epw', hoys, north, high_sky_density
        )

    study = RadiationStudy(
        sky_matrix=sky_matrix, study_mesh=study_mesh,
        context_geometry=context_geo, offset_distance=offset_distance
    )

    study.compute()
    vis_set = study.to_vis_set(plot_irradiance=avg_irr, include_context=display_context)

    output_folder = pathlib.Path('results')
    output_folder.mkdir(parents=True, exist_ok=True)

    output_file = output_folder.joinpath('results.json')
    if avg_irr:
        output_file.write_text(json.dumps(study.irradiance_values))
    else:
        output_file.write_text(json.dumps(study.radiation_values))

    vsf_file = output_folder.joinpath('output.vsf')
    vsf_file.write_text(json.dumps(vis_set.to_dict()))
