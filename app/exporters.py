try:
    import ujson as json
except ImportError:
    import json

try:
    from umqtt.simple import MQTTClient
except ImportError:
    MQTTClient = None


class BaseExporter:
    def publish(self, payload):
        raise NotImplementedError


class MqttExporter(BaseExporter):
    def __init__(
        self,
        enabled=False,
        broker=None,
        topic="weather/sensors",
        client_id="pico2-weather",
        port=1883,
        user=None,
        password=None,
        keepalive=60,
        ssl=False,
        qos=0,
        retain=False,
    ):
        self.enabled = enabled
        self.broker = broker
        self.topic = topic
        self.client_id = client_id
        self.port = port
        self.user = user
        self.password = password
        self.keepalive = keepalive
        self.ssl = ssl
        self.qos = qos
        self.retain = retain
        self._client = None

    def _connect(self):
        if MQTTClient is None:
            raise RuntimeError("umqtt.simple is not available")
        if not self.broker:
            raise RuntimeError("MQTT broker is not configured")
        if self._client:
            return self._client

        client = MQTTClient(
            client_id=self.client_id,
            server=self.broker,
            port=self.port,
            user=self.user,
            password=self.password,
            keepalive=self.keepalive,
            ssl=self.ssl,
        )
        client.connect()
        self._client = client
        return client

    def publish(self, payload):
        if not self.enabled:
            return False

        topic = self.topic if isinstance(self.topic, bytes) else str(self.topic).encode()
        message = json.dumps(payload)
        if not isinstance(message, bytes):
            message = message.encode()
        client = self._connect()
        try:
            client.publish(topic, message, retain=self.retain, qos=self.qos)
        except Exception:
            self._client = None
            client = self._connect()
            client.publish(topic, message, retain=self.retain, qos=self.qos)
        return True


class LoRaWanExporter(BaseExporter):
    def __init__(self, enabled=False, port=1):
        self.enabled = enabled
        self.port = port

    def publish(self, payload):
        if not self.enabled:
            return False
        # TODO: Integrate your LoRaWAN modem/stack here.
        _ = json.dumps(payload)
        return True


class ExportManager:
    def __init__(self, exporters=None):
        self._exporters = exporters or []

    def publish_all(self, payload):
        results = {}
        for exporter in self._exporters:
            name = exporter.__class__.__name__
            try:
                results[name] = exporter.publish(payload)
            except Exception as exc:
                results[name] = str(exc)
        return results
