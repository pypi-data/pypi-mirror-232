from pollination.ladybug_radiance.radiation import IncidentRadiation
from queenbee.plugin.function import Function


def test_incident_radiation():
    function = IncidentRadiation().queenbee
    assert function.name == 'incident-radiation'
    assert isinstance(function, Function)
