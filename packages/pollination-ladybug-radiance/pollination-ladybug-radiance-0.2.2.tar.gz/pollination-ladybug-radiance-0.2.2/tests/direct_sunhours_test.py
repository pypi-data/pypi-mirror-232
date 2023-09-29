from pollination.ladybug_radiance.direct_sunhours import DirectSunHours
from queenbee.plugin.function import Function


def test_direct_sun_hours():
    function = DirectSunHours().queenbee
    assert function.name == 'direct-sun-hours'
    assert isinstance(function, Function)
