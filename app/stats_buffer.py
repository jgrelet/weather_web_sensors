class CircularStatsBuffer:
    EXCLUDED_NUMERIC_KEYS = {
        "timestamp",
        "rain_mm_total",
        "wind_dir_deg",
        "wind_dir_raw",
    }

    SUM_KEYS = {
        "rain_tips",
        "rain_mm",
        "wind_pulses",
    }

    def __init__(self, capacity):
        self.capacity = max(1, int(capacity))
        self.reset()

    def reset(self):
        self._numeric = {}
        self._latest = {}
        self._sample_count = 0

    def add(self, sample):
        if not sample:
            return

        self._sample_count += 1
        for key, value in sample.items():
            self._latest[key] = value
            if not self._is_numeric(value) or key in self.EXCLUDED_NUMERIC_KEYS:
                continue

            values = self._numeric.get(key)
            if values is None:
                values = []
                self._numeric[key] = values
            values.append(float(value))
            if len(values) > self.capacity:
                values.pop(0)

    def has_samples(self):
        return self._sample_count > 0

    def build_snapshot(self, window_seconds, closed_at=None):
        snapshot = {}
        for key, value in self._latest.items():
            if key not in self._numeric:
                snapshot[key] = value

        snapshot["aggregation_window_seconds"] = int(window_seconds)
        snapshot["aggregation_samples"] = self._sample_count
        if closed_at is not None:
            snapshot["timestamp"] = closed_at

        for key, values in self._numeric.items():
            if not values:
                continue

            sample_size = len(values)
            total = sum(values)
            mean = total / sample_size
            median = self._median(values)
            stddev = self._stddev(values, mean)

            if key in self.SUM_KEYS:
                snapshot[key] = self._round(total)
                snapshot[key + "_sum"] = self._round(total)
            else:
                snapshot[key] = self._round(mean)

            snapshot[key + "_mean"] = self._round(mean)
            snapshot[key + "_median"] = self._round(median)
            snapshot[key + "_stddev"] = self._round(stddev)
            snapshot[key + "_samples"] = sample_size

        return snapshot

    def _median(self, values):
        ordered = sorted(values)
        middle = len(ordered) // 2
        if len(ordered) % 2:
            return ordered[middle]
        return (ordered[middle - 1] + ordered[middle]) / 2

    def _stddev(self, values, mean):
        if len(values) < 2:
            return 0.0
        variance = sum((value - mean) * (value - mean) for value in values) / len(values)
        return variance ** 0.5

    def _round(self, value):
        if int(value) == value:
            return int(value)
        return round(value, 3)

    def _is_numeric(self, value):
        return isinstance(value, (int, float)) and not isinstance(value, bool)
