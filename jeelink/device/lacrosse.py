from jeelink.device.device import JeeLinkDevice


class LaCrosseDevice(JeeLinkDevice):
    def __init__(self, jeelink, device_id):
        super().__init__(jeelink, device_id)
        self._sensor_type = 0
        self._new_battery = None
        self._temperature = 0
        self._humidity = 0
        self._low_battery = None

    @property
    def sensor_type(self):
        return self._sensor_type

    @property
    def new_battery(self):
        return self._new_battery

    @property
    def temperature(self):
        return self._temperature

    @property
    def humidity(self):
        return self._humidity

    @property
    def low_battery(self):
        return self._low_battery
