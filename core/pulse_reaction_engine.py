"""
IDC Core - Pulse Reaction Engine
Manages real-time electrical/current pulses and telemetry in a volatile RAM ring buffer.
Executes O(1) involuntary reflex reactions when thresholds are crossed,
bypassing LLM and disk I/O to guarantee sub-millisecond safety responses.
"""

import collections
import time
from typing import Any, Dict, List, Optional
from contracts.pulse import ReactionPulse, PulseReactionRule, ReflexResponse


class PulseReactionEngine:
    """
    Subcortical/reflexive reaction engine operating on active pre-cached pulses.
    Maintains a bounded in-memory buffer without disk persistence.
    """

    def __init__(self, buffer_size: int = 128):
        self.buffer_size = buffer_size
        self._pulse_ring_buffer: collections.deque = collections.deque(maxlen=buffer_size)
        self._rules_by_channel: Dict[str, List[PulseReactionRule]] = {}
        self._last_trigger_times: Dict[str, float] = {}
        self._total_pulses_received: int = 0
        self._total_reflexes_fired: int = 0

        # Install default reflex rules (e.g. thermal spike, voltage rail failure, memory surge)
        self._install_default_reflex_rules()

    def _install_default_reflex_rules(self) -> None:
        """Pre-caches critical reflex rules into RAM."""
        defaults = [
            PulseReactionRule(
                id="reflex_overvoltage_rail",
                channel="voltage_rail",
                threshold_amplitude=12.8,  # >12.8V is lethal for electronics
                trigger_condition="gt",
                reflex_action="trip_breaker_and_isolate_rail",
                cooldown_ms=10.0,
                energy_cost=0.01,
            ),
            PulseReactionRule(
                id="reflex_thermal_spike",
                channel="thermal_spike",
                threshold_amplitude=85.0,  # >85 Celsius critical junction
                trigger_condition="gt",
                reflex_action="throttle_clock_and_divert_load",
                cooldown_ms=50.0,
                energy_cost=0.02,
            ),
            PulseReactionRule(
                id="reflex_network_flood",
                channel="network_io",
                threshold_amplitude=1000.0, # packets/ms flood
                trigger_condition="gt",
                reflex_action="engage_rate_limiter_shield",
                cooldown_ms=100.0,
                energy_cost=0.05,
            ),
        ]
        for rule in defaults:
            self.register_reflex_rule(rule)

    def register_reflex_rule(self, rule: PulseReactionRule) -> None:
        """Registers a reflex rule in the pre-cached memory table."""
        if rule.channel not in self._rules_by_channel:
            self._rules_by_channel[rule.channel] = []
        self._rules_by_channel[rule.channel].append(rule)

    def receive_pulse(self, pulse: ReactionPulse) -> ReflexResponse:
        """
        Receives an active current or telemetry pulse, buffers it in volatile RAM,
        and evaluates reflex conditions in O(1) time.
        """
        t0 = time.perf_counter()
        self._total_pulses_received += 1
        self._pulse_ring_buffer.append(pulse)

        # Lookup rules for this specific channel
        rules = self._rules_by_channel.get(pulse.channel, [])
        now_ms = time.time() * 1000.0

        for rule in rules:
            if not rule.active:
                continue

            # Check cooldown
            last_t = self._last_trigger_times.get(rule.id, 0.0)
            if (now_ms - last_t) < rule.cooldown_ms:
                continue

            # Evaluate condition
            matched = False
            if rule.trigger_condition == "gt" and pulse.amplitude > rule.threshold_amplitude:
                matched = True
            elif rule.trigger_condition == "lt" and pulse.amplitude < rule.threshold_amplitude:
                matched = True
            elif rule.trigger_condition == "gradient_spike" and abs(pulse.gradient) > rule.threshold_amplitude:
                matched = True

            if matched:
                self._last_trigger_times[rule.id] = now_ms
                self._total_reflexes_fired += 1
                latency = (time.perf_counter() - t0) * 1000.0

                return ReflexResponse(
                    triggered=True,
                    rule_id=rule.id,
                    action=rule.reflex_action,
                    latency_ms=round(latency, 4),
                    energy_cost=rule.energy_cost,
                    triggering_pulse_id=pulse.id,
                    reason=f"Pulse on channel '{pulse.channel}' value {pulse.amplitude} breached threshold {rule.threshold_amplitude}",
                )

        latency = (time.perf_counter() - t0) * 1000.0
        return ReflexResponse(
            triggered=False,
            latency_ms=round(latency, 4),
            energy_cost=0.0,
            triggering_pulse_id=pulse.id,
            reason="Within nominal bounds (no reflex required)",
        )

    def get_recent_pulses(self, limit: int = 10) -> List[ReactionPulse]:
        """Returns the most recent active pulses from the volatile ring buffer."""
        return list(self._pulse_ring_buffer)[-limit:]

    def clear_volatile_buffer(self) -> None:
        """Purges volatile buffer to enforce zero long-term bloat."""
        self._pulse_ring_buffer.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "total_pulses_received": self._total_pulses_received,
            "total_reflexes_fired": self._total_reflexes_fired,
            "buffered_pulses_count": len(self._pulse_ring_buffer),
            "registered_rules_count": sum(len(r) for r in self._rules_by_channel.values()),
        }
