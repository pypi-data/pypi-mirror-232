import inspect
from dataclasses import dataclass
from pollination_dsl.function import Function, script, Inputs, Outputs

from .scripts import direct_sunhours


@dataclass
class DirectSunHours(Function):
    """Calculate direct sun hours."""

    vectors = Inputs.file(
        description='A file that includes sun vectors.', path='sun_vectors.txt'
    )

    offset_dist = Inputs.float(
        description='Number in model units for the distance to move points from '
        'the surfaces of the input geometry.', default=0.01,
        spec={'type': 'number', 'maximum': 1.0, 'minimum': 0.001}
    )

    timestep = Inputs.int(
        description='A number for vectors timesteps', default=1,
        spec={'type': 'number', 'maximum': 60, 'minimum': 1}
    )

    study_mesh = Inputs.file(
        description='Path to a JSON file for input study mesh in Ladybug Geometry '
        'format.', path='input_geo.json'
    )

    context_mesh = Inputs.file(
        description='Path to a JSON file for input context mesh in Ladybug Geometry '
        'format.', path='context_geo.json', optional=True
    )

    display_context = Inputs.bool(
        description='Boolean to note whether the context geometry should be included '
        'in the output visualization.',
        default=False
    )

    @script
    def run_direct_sunlight(self):
        return inspect.getsource(direct_sunhours)

    direct_sunlight_values = Outputs.file(
        description='direct sun hours values', path='results/results.json'
    )

    visualization_set = Outputs.file(
        description='Results visualization set', path='results/output.vsf'
    )
