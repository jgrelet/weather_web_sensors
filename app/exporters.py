try:
    import ujson as json
except ImportError:
    import json

try:
    import usocket as socket
except ImportError:
    import socket

try:
    from umqtt.simple import MQTTClient
except ImportError:
    MQTTClient = None


class BaseExporter:
    def publish(self, payload, route=None):
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

    def publish(self, payload, route=None):
        if not self.enabled:
            return False

        topic_name = self.topic
        if route:
            topic_name = route.get("topic", topic_name)
        topic = topic_name if isinstance(topic_name, bytes) else str(topic_name).encode()
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


class SerialExporter(BaseExporter):
    def __init__(self, enabled=False, prefix="JSON"):
        self.enabled = enabled
        self.prefix = prefix

    def publish(self, payload, route=None):
        if not self.enabled:
            return False
        message = json.dumps(payload)
        prefix = self.prefix
        if route:
            prefix = route.get("prefix", prefix)
        if prefix:
            print("{} {}".format(prefix, message))
        else:
            print(message)
        return True


class UdpExporter(BaseExporter):
    def __init__(self, enabled=False, host=None, port=9999):
        self.enabled = enabled
        self.host = host
        self.port = port
        self._addr = None
        self._sock = None

    def _connect(self):
        if not self.host:
            raise RuntimeError("UDP host is not configured")
        if self._sock and self._addr:
            return self._sock, self._addr
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._addr = addr
        return self._sock, self._addr

    def publish(self, payload, route=None):
        if not self.enabled:
            return False
        message = json.dumps(payload)
        if not isinstance(message, bytes):
            message = message.encode()
        sock, addr = self._connect()
        try:
            sock.sendto(message, addr)
        except Exception:
            self._sock = None
            self._addr = None
            sock, addr = self._connect()
            sock.sendto(message, addr)
        return True


class LoRaWanExporter(BaseExporter):
    def __init__(self, enabled=False, port=1):
        self.enabled = enabled
        self.port = port

    def publish(self, payload, route=None):
        if not self.enabled:
            return False
        # TODO: Integrate your LoRaWAN modem/stack here.
        _ = json.dumps(payload)
        return True


class ExportManager:
    def __init__(self, exporters=None):
        self._exporters = exporters or []

    def publish_all(self, payload, route=None):
        results = {}
        for exporter in self._exporters:
            name = exporter.__class__.__name__
            try:
                results[name] = exporter.publish(payload, route=route)
            except Exception as exc:
                results[name] = str(exc)
        return results

    def publish_due(self, payload, route=None):
        results = {}
        for exporter in self._exporters:
            name = exporter.__class__.__name__
            if not getattr(exporter, "enabled", False):
                results[name] = False
                continue
            try:
                results[name] = exporter.publish(payload, route=route)
            except Exception as exc:
                results[name] = str(exc)
        return results
