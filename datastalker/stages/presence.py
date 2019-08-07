from time import time

from datastalker.pipeline import (
    Message,
    Stage,
    Pipeline
)

class _State:
    def __init__(self, key, now, packet):
        "Create state based on the packet data"
        self.first_seen = now
        self.last_logged = now
        self.key = key

        self.src_oui = packet['src_oui']
        self.src = packet['src']

        # Aggregations
        self.ssids = set()
        self.tags = set()
        self.destinations = set()

        # Timestamp -> signal strength
        self.strengths = {}

        self.update(packet, now)
        if packet['ssid']:
            self.ssids.add(packet['ssid'])

    def get_avg_strength(self):
        "Calculate average strength"
        strengths = list(self.strengths.values())
        avg_strength = sum(strengths) / len(strengths)
        return avg_strength

    def __repr__(self):
        avg_str = self.get_avg_strength()
        seen = self.last_seen - self.first_seen
        s = ("<PresenceState src={0.src}/{0.src_oui} "
             "seen={2:0.2f}s "
             "str={1} "
             "tags={0.tags} "
             "ssids={0.ssids}>")
        return s.format(self, avg_str, seen)

    def update(self, packet, now):
        "Update with new packet"
        self.last_seen = now

        if packet['ssid']:
            self.ssids.add(packet['ssid'])

        if packet['dst']:
            self.destinations.add(packet['dst'])

        for tag in packet['tags']:
            self.tags.add(tag)

        if len(self.strengths) < 1000:
            self.strengths[now] = packet['strength']

class Event(Message):
    """
    Represents a presence event.
    """
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    ABSENT = "ABSENT"

    def __init__(self, event_type, state):
        self.event_type = event_type
        self.src = state.src
        self.state = state

    def __repr__(self):
        s = "<Event {0.src} {0.event_type} {0.state}>"
        return s.format(self)


@Pipeline.register_stage('presence')
class PresenceStage(Stage):
    """
    """
    def __init__(self, stats, key, absence_timeout, active_timeout):
        self.stats = stats
        self.key = key

        # How long to wait before announcing absence
        self.absence_timeout = absence_timeout

        # How often to log when still active
        self.active_timeout = active_timeout

        self.cleanup_ts = time()

        # {key: State, ...}
        self.states = {}

    def get_key(self, packet):
        "Create a key for given packet"
        return tuple(
            packet[field]
            for field in self.key
        )

    def handle_new(self, packet, key):
        now = time()
        state = _State(key, now, packet)
        # Add to cache
        self.states[key] = state

        event = Event(Event.NEW, state)
        self.log.info("EVENT NEW key %r ev %r", key, event)
        return [event]

    def handle_active(self, packet, key, state):
        "Already seen, is active"
        now = time()
        state.update(packet, now)

        events = []
        if state.last_logged + self.active_timeout <= now:
            event = Event(Event.ACTIVE, state)
            events.append(event)
            state.last_logged = now
            self.log.info("EVENT LOG ACTIVE %r", event)

        return events

    def handle_absent(self):
        now = time()
        last_active = now - self.absence_timeout
        absent = [
            key
            for key, state in self.states.items()
            if state.last_seen < last_active
        ]

        events = [
            Event(Event.ABSENT, self.states[key])
            for key in absent
        ]

        for key in absent:
            del self.states[key]

        if absent:
            self.log.info("EVENT DEL ABSENT %r", events)

        return events

    def handle(self, packet):
        "Handle packet"
        key = self.get_key(packet)
        state = self.states.get(key)

        if state is None:
            events = self.handle_new(packet, key)
        else:
            events = self.handle_active(packet, key, state)

        now = time()
        if self.cleanup_ts + 1 <= now:
            events += self.handle_absent()
            self.cleanup_ts = now

        if not events:
            return None
        else:
            return events

    @classmethod
    def from_config(cls, config, stats):
        cfg = {
            'absence_timeout': config.get('absence_timeout', 60),
            'active_timeout': config.get('active_timeout', 120),
            'key': config.get('key', ['src']),
        }
        stage = PresenceStage(stats, **cfg)
        print("CREATED")
        return stage

