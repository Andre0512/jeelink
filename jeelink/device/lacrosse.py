class LaCrosseDevice:
    def __init__(self, jeelink, device_id):
        self._sensor_id = device_id
        self._sensor_type = 0
        self._new_battery = None
        self._temperature = 0
        self._humidity = 0
        self._low_battery = None
        self._jeelink = jeelink

    @property
    def sensor_id(self):
        return self._sensor_id

    def set_sensor_id(self, sensor_id):
        self._sensor_id = sensor_id

    @property
    def sensor_type(self):
        return self._sensor_type

    def set_sensor_type(self, sensor_type):
        self._sensor_type = sensor_type

    @property
    def new_battery(self):
        return self._new_battery

    def set_new_battery(self, new_battery):
        self._new_battery = new_battery

    @property
    def temperature(self):
        return self._temperature

    def set_temperature(self, temperature):
        self._temperature = temperature

    @property
    def humidity(self):
        return self._humidity

    def set_humidity(self, humidity):
        self._humidity = humidity

    @property
    def low_battery(self):
        return self._low_battery

    def set_low_battery(self, low_battery):
        self._low_battery = low_battery
