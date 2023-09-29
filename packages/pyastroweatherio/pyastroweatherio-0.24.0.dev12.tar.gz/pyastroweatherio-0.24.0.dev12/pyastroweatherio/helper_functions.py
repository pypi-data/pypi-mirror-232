""" Contains Helper functions for AstroWeather."""
from datetime import datetime
# , timedelta
import logging
# import ephem
# from ephem import degree
# from math import degrees as deg
import pytz

# Astroplan
import warnings
from pytz import timezone
from astropy import units as u
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astroplan import Observer
from astroplan.exceptions import TargetAlwaysUpWarning, TargetNeverUpWarning

# The introduction of the module [timezonefinder](https://github.com/jannikmi/timezonefinder)
# with it's nested dependency to [py-h3](https://github.com/uber/h3-py) failed while compiling
# the `c`-module h3 on some home assistant deployment variants (e.g. Home Assistant
# Operating System on RPi).
# from timezonefinder import TimezoneFinder
from pyastroweatherio.const import (
    DEFAULT_ELEVATION,
    DEFAULT_TIMEZONE,
    HOME_LATITUDE,
    HOME_LONGITUDE,
    CIVIL_TWILIGHT,
    CIVIL_DUSK_DAWN,
    NAUTICAL_TWILIGHT,
    NAUTICAL_DUSK_DAWN,
    ASTRONOMICAL_TWILIGHT,
    ASTRONOMICAL_DUSK_DAWN,
)

_LOGGER = logging.getLogger(__name__)


class ConversionFunctions:
    """Convert between different Weather Units."""

    async def epoch_to_datetime(self, value) -> str:
        """Converts EPOC time to Date Time String."""
        return datetime.datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d %H:%M:%S")

    async def anchor_timestamp(self, value) -> datetime:
        """Converts the datetime string from 7Timer to DateTime."""
        return datetime.strptime(value, "%Y%m%d%H")


class AstronomicalRoutines:
    """Calculate different astronomical objects"""

    def __init__(
        self,
        latitude=HOME_LATITUDE,
        longitude=HOME_LONGITUDE,
        elevation=DEFAULT_ELEVATION,
        timezone_info=DEFAULT_TIMEZONE,
        forecast_time=datetime.utcnow(),
    ):
        self._longitude = longitude
        self._latitude = latitude
        self._elevation = elevation
        self._timezone_info = timezone_info
        # tz_find = TimezoneFinder()
        # self._timezone_info = tz_find.timezone_at(lng=longitude, lat=latitude)
        _LOGGER.debug("Timezone: %s", self._timezone_info)
        self._forecast_time = forecast_time

        self._sun_observer = None
        self._sun_observer_nautical = None
        self._sun_observer_astro = None
        self._moon_observer = None
        self._sun_next_rising_civil = None
        self._sun_next_setting_civil = None
        self._sun_next_rising_nautical = None
        self._sun_next_setting_nautical = None
        self._sun_next_rising_astro = None
        self._sun_next_setting_astro = None
        self._sun_altitude = None
        self._sun_azimuth = None
        self._moon_next_rising = None
        self._moon_next_setting = None
        self._moon_altitude = None
        self._moon_azimuth = None
        self._moon_illumination = None
        self._sun = None
        self._moon = None

    async def calc(
        self,
        longitude,
        latitude,
        elevation,
        tz,
        pressure=0,
        relative_humidity=0,
        temperature=0,
        observation_date=None,
    ):
        # Our observer
        location = EarthLocation.from_geodetic(longitude, latitude, elevation * u.m)

        observer = Observer(
            name="Observer",
            location=location,
            pressure=pressure * u.bar,
            relative_humidity=relative_humidity,
            temperature=temperature * u.deg_C,
            timezone=timezone(tz),
        )

        # Calculate tonights night unless a date is given
        if observation_date is None:
            # time = (
            #     Time(
            #         datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
            #         scale="utc",
            #         location=observer.location,
            #     )
            #     + 12 * u.hour
            # )
            time = Time(
                datetime.utcnow(),
                scale="utc",
                location=observer.location,
            )
        else:
            time = (
                Time(
                    datetime.strptime(observation_date, "%m/%d/%y").replace(hour=0, minute=0, second=0, microsecond=0),
                    scale="utc",
                    location=observer.location,
                )
                + 12 * u.hour
            )
        _LOGGER.debug("Astronomical calculations for: {0} UTC".format(time.strftime("%m/%d/%Y %H:%M:%S")))
        _LOGGER.debug("EarthLocation: {0} {1} {2}".format(longitude, latitude, elevation * u.m))


        darkness = ""

        with warnings.catch_warnings(record=True) as w:
            observer.sun_set_time(time, which="next", horizon=-6 * u.deg)
            if len(w):
                if issubclass(w[-1].category, TargetAlwaysUpWarning):
                    _LOGGER.debug("Sun is not setting civically")
                    self._sun_next_setting_civil = await self.utc_to_local((time + 1 * u.day).to_datetime())
                    self._sun_next_rising_civil = await self.utc_to_local(time.to_datetime())
                w.clear()
            else:
                darkness = "civil"
                sun_next_setting_civil = observer.sun_set_time(time=time, which='next', horizon=-6 * u.deg)
                sun_next_rising_civil = observer.sun_rise_time(time=time, which='next', horizon=-6 * u.deg)

                # Compatibility
                self._sun_next_setting_civil = await self.utc_to_local(sun_next_setting_civil.to_datetime())
                self._sun_next_rising_civil = await self.utc_to_local(sun_next_rising_civil.to_datetime())

        with warnings.catch_warnings(record=True) as w:
            observer.sun_set_time(time, which="next", horizon=-12 * u.deg)
            if len(w):
                if issubclass(w[-1].category, TargetAlwaysUpWarning):
                    _LOGGER.debug("Sun is not setting nautically")
                    w.clear()
            else:
                darkness = "nautical"
                sun_next_setting_nautical = observer.sun_set_time(time=time, which='next', horizon=-12 * u.deg)
                sun_next_rising_nautical = observer.sun_rise_time(time=time, which='next', horizon=-12 * u.deg)

                # Compatibility
                self._sun_next_setting_nautical = await self.utc_to_local(sun_next_setting_nautical.to_datetime())
                self._sun_next_rising_nautical = await self.utc_to_local(sun_next_rising_nautical.to_datetime())

        with warnings.catch_warnings(record=True) as w:
            observer.sun_set_time(time, which="next", horizon=-18 * u.deg)
            if len(w):
                if issubclass(w[-1].category, TargetAlwaysUpWarning):
                    _LOGGER.debug("Sun is not setting astronomically")
                    w.clear()
            else:
                darkness = "astronomical"
                sun_next_setting_astronomical = observer.sun_set_time(
                    time=time, which='next', horizon=-18 * u.deg
                )
                sun_next_rising_astronomical = observer.sun_rise_time(
                    time=time, which='next', horizon=-18 * u.deg
                )

                # Compatibility
                self._sun_next_setting_astro = await self.utc_to_local(sun_next_setting_astronomical.to_datetime())
                self._sun_next_rising_astro = await self.utc_to_local(sun_next_rising_astronomical.to_datetime())

        with warnings.catch_warnings(record=True) as w:
            observer.moon_set_time(time, which="next", horizon=0 * u.deg)
            if len(w):
                if issubclass(w[-1].category, TargetAlwaysUpWarning):
                    _LOGGER.debug("Moon is not setting civically")
                    w.clear()
            else:
                # moon_next_setting_civil, moon_next_rising_civil = observer.tonight(
                #     time=time, horizon=0 * u.deg
                # )
                moon_next_setting_civil = observer.moon_set_time(time=time, which='next', horizon=0 * u.deg)
                moon_next_rising_civil = observer.moon_rise_time(time=time, which='next', horizon=0 * u.deg)

                # Compatibility
                self._moon_next_setting = await self.utc_to_local(moon_next_setting_civil.to_datetime())
                self._moon_next_rising = await self.utc_to_local(moon_next_rising_civil.to_datetime())
                
        _LOGGER.debug("Darkness: {0}".format(darkness))
        _LOGGER.debug("Sun set local {0}: {1}".format("astronomical", self._sun_next_setting_astro))
        _LOGGER.debug("Sun rise local {0}: {1}".format("astronomical", self._sun_next_rising_astro))
        _LOGGER.debug("Sun set local {0}: {1}".format("nautical", self._sun_next_setting_nautical))
        _LOGGER.debug("Sun rise local {0}: {1}".format("nautical", self._sun_next_rising_nautical))
        _LOGGER.debug("Sun set local {0}: {1}".format("civil", self._sun_next_setting_civil))
        _LOGGER.debug("Sun rise local {0}: {1}".format("civil", self._sun_next_rising_civil))
        _LOGGER.debug("Moon set local {0}: {1}".format("civil", self._moon_next_setting))
        _LOGGER.debug("Moon rise local {0}: {1}".format("civil", self._moon_next_rising))

        altaz_sun = observer.sun_altaz(Time.now())
        # Compatibility
        self._sun_altitude = altaz_sun.alt.degree
        self._sun_azimuth = altaz_sun.az.degree
        # _LOGGER.debug("Sun alt: {0.alt}, az: {0.az}".format(altaz_sun))

        altaz_moon = observer.moon_altaz(Time.now())
        # Compatibility
        self._moon_altitude = altaz_moon.alt.degree
        self._moon_azimuth = altaz_moon.az.degree
        # _LOGGER.debug("Moon alt: {0.alt}, az: {0.az}".format(altaz_moon))

        self._moon_illumination = observer.moon_illumination(self._sun_next_setting_civil) * 100
        _LOGGER.debug("Moon illumination: {:.0f}%".format(self._moon_illumination))

    async def utc_to_local(self, utc_dt):
        """Localizes the datetime"""
        local_tz = pytz.timezone(self._timezone_info)
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)

    async def utc_to_local_diff(self):
        """returns the UTC Offset"""
        local = await self.utc_to_local(datetime.now())
        return local.utcoffset().seconds // 3600

    async def need_update(self):
        localtime = await self.utc_to_local(datetime.utcnow())
        if (
            self._sun_next_setting_civil is None
            or self._sun_next_setting_nautical is None
            or self._sun_next_setting_astro is None
            or self._sun_next_rising_astro is None
            or self._sun_next_rising_nautical is None
            or self._sun_next_rising_civil is None
            or self._moon_next_rising is None
            or self._moon_next_setting is None
            or localtime > self._sun_next_setting_civil
            or localtime > self._sun_next_setting_nautical
            or localtime > self._sun_next_setting_astro
            or localtime > self._sun_next_rising_astro
            or localtime > self._sun_next_rising_nautical
            or localtime > self._sun_next_rising_civil
            or localtime > self._moon_next_rising
            or localtime > self._moon_next_setting
        ):
            await self.calc(self._longitude, self._latitude, self._elevation, self._timezone_info)
        else:
            _LOGGER.debug("Astronomical calculations are up to date")

    async def sun_next_rising(self) -> datetime:
        """Returns sun next rising"""
        if self._sun_next_rising_astro is not None:
            return self._sun_next_rising_astro
        if self._sun_next_rising_nautical is not None:
            return self._sun_next_rising_nautical
        if self._sun_next_rising_civil is not None:
            return self._sun_next_rising_civil

    async def sun_next_rising_civil(self) -> datetime:
        """Returns sun next civil rising"""
        if self._sun_next_rising_civil is not None:
            return self._sun_next_rising_civil

    async def sun_next_rising_nautical(self) -> datetime:
        """Returns sun next nautical rising"""
        if self._sun_next_rising_nautical is not None:
            return self._sun_next_rising_nautical

    async def sun_next_rising_astro(self) -> datetime:
        """Returns sun next astronomical rising"""
        if self._sun_next_rising_astro is not None:
            return self._sun_next_rising_astro

    async def sun_next_setting(self) -> datetime:
        """Returns sun next setting"""
        if self._sun_next_setting_astro is not None:
            return self._sun_next_setting_astro
        if self._sun_next_setting_nautical is not None:
            return self._sun_next_setting_nautical
        if self._sun_next_setting_civil is not None:
            return self._sun_next_setting_civil

    async def sun_next_setting_civil(self) -> datetime:
        """Returns sun next civil setting"""
        if self._sun_next_setting_civil is not None:
            return self._sun_next_setting_civil

    async def sun_next_setting_nautical(self) -> datetime:
        """Returns sun next nautical setting"""
        if self._sun_next_setting_nautical is not None:
            return self._sun_next_setting_nautical

    async def sun_next_setting_astro(self) -> datetime:
        """Returns sun next astronomical setting"""
        if self._sun_next_setting_astro is not None:
            return self._sun_next_setting_astro

    async def sun_altitude(self) -> float:
        """Returns the sun altitude"""
        if self._sun_altitude is not None:
            return self._sun_altitude

    async def sun_azimuth(self) -> float:
        """Returns the sun azimuth"""
        if self._sun_azimuth is not None:
            return self._sun_azimuth

    async def moon_next_rising(self) -> datetime:
        """Returns moon next rising"""
        if self._moon_next_rising is not None:
            return self._moon_next_rising

    async def moon_next_setting(self) -> datetime:
        """Returns moon next setting"""
        if self._moon_next_setting is not None:
            return self._moon_next_setting

    async def moon_phase(self) -> float:
        """Returns the moon phase"""
        return self._moon_illumination

    async def moon_altitude(self) -> float:
        """Returns the moon altitude"""
        if self._moon_altitude is not None:
            return self._moon_altitude

    async def moon_azimuth(self) -> float:
        """Returns the moon azimuth"""
        if self._moon_azimuth is not None:
            return self._moon_azimuth
