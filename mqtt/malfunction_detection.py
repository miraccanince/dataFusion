"""
Malfunction Detection Rules for Raspberry Pi
=============================================

Two simple rules to detect malfunctioning of the Raspberry Pi
based on CPU performance data from MQTT stream.

Assignment: Part 1 - Data Stream Management System (15%)

Usage:
    python3 malfunction_detection.py [--broker BROKER_IP]
"""

import paho.mqtt.client as mqtt
import json
import argparse
from datetime import datetime
from collections import deque
import time


class MalfunctionDetector:
    """
    Monitors CPU performance and detects potential malfunctions

    Detection Rules:
    1. **High Temperature Rule**: CPU temperature > 80°C for >10 seconds
       - Indicates thermal throttling risk
       - May lead to performance degradation or shutdown

    2. **Memory Exhaustion Rule**: Memory usage > 90% for >10 seconds
       - Indicates out-of-memory risk
       - May cause system freeze or crashes
    """

    def __init__(self, broker='localhost', port=1883):
        """
        Initialize malfunction detector

        Args:
            broker: MQTT broker IP address
            port: MQTT broker port
        """
        self.broker = broker
        self.port = port

        # Detection thresholds
        self.HIGH_TEMP_THRESHOLD = 80.0  # °C
        self.HIGH_MEMORY_THRESHOLD = 90.0  # %
        self.ALARM_DURATION = 10.0  # seconds

        # State tracking
        self.high_temp_start = None
        self.high_memory_start = None

        # Alarm states
        self.temp_alarm_active = False
        self.memory_alarm_active = False

        # Statistics
        self.message_count = 0
        self.temp_alarms_triggered = 0
        self.memory_alarms_triggered = 0

        # Recent data for context
        self.recent_temps = deque(maxlen=60)  # Last 60 readings
        self.recent_memory = deque(maxlen=60)

        # MQTT topics
        self.topic_cpu = "dataFusion/cpu/performance"
        self.topic_alerts = "dataFusion/alerts/malfunction"

        # MQTT client
        self.client = mqtt.Client(client_id="malfunction_detector")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected"""
        if rc == 0:
            self.connected = True
            print(f"✓ Connected to MQTT broker at {self.broker}:{self.port}")

            # Subscribe to CPU performance
            client.subscribe(self.topic_cpu, qos=0)
            print(f"✓ Subscribed to: {self.topic_cpu}")
            print(f"\n🔍 Malfunction Detection Rules:")
            print(f"   1. High Temperature: CPU > {self.HIGH_TEMP_THRESHOLD}°C for {self.ALARM_DURATION}s")
            print(f"   2. Memory Exhaustion: Memory > {self.HIGH_MEMORY_THRESHOLD}% for {self.ALARM_DURATION}s")
            print(f"\n✓ Monitoring started...\n")
        else:
            print(f"✗ Connection failed with code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        self.connected = False
        if rc != 0:
            print(f"⚠ Unexpected disconnection. Code: {rc}")

    def check_high_temperature(self, temperature):
        """
        Rule 1: Detect sustained high CPU temperature

        Args:
            temperature: Current CPU temperature in °C

        Returns:
            bool: True if malfunction detected
        """
        current_time = time.time()

        if temperature > self.HIGH_TEMP_THRESHOLD:
            if self.high_temp_start is None:
                self.high_temp_start = current_time
                print(f"⚠ WARNING: High temperature detected ({temperature:.1f}°C)")

            # Check duration
            duration = current_time - self.high_temp_start

            if duration >= self.ALARM_DURATION and not self.temp_alarm_active:
                self.temp_alarm_active = True
                self.temp_alarms_triggered += 1
                return True

        else:
            # Temperature back to normal
            if self.temp_alarm_active:
                print(f"✓ Temperature back to normal ({temperature:.1f}°C)")
            self.high_temp_start = None
            self.temp_alarm_active = False

        return False

    def check_memory_exhaustion(self, memory_percent):
        """
        Rule 2: Detect sustained high memory usage

        Args:
            memory_percent: Current memory usage in %

        Returns:
            bool: True if malfunction detected
        """
        current_time = time.time()

        if memory_percent > self.HIGH_MEMORY_THRESHOLD:
            if self.high_memory_start is None:
                self.high_memory_start = current_time
                print(f"⚠ WARNING: High memory usage detected ({memory_percent:.1f}%)")

            # Check duration
            duration = current_time - self.high_memory_start

            if duration >= self.ALARM_DURATION and not self.memory_alarm_active:
                self.memory_alarm_active = True
                self.memory_alarms_triggered += 1
                return True

        else:
            # Memory back to normal
            if self.memory_alarm_active:
                print(f"✓ Memory usage back to normal ({memory_percent:.1f}%)")
            self.high_memory_start = None
            self.memory_alarm_active = False

        return False

    def publish_alert(self, alert_type, details):
        """
        Publish malfunction alert to MQTT

        Args:
            alert_type: Type of alert ('temperature' or 'memory')
            details: Alert details
        """
        alert_msg = {
            'timestamp': datetime.utcnow().isoformat(),
            'alert_type': alert_type,
            'severity': 'CRITICAL',
            'details': details
        }

        self.client.publish(
            self.topic_alerts,
            json.dumps(alert_msg),
            qos=1,  # QoS 1 for important alerts
            retain=True  # Retain for new subscribers
        )

        print(f"\n🚨 ALERT PUBLISHED: {alert_type.upper()}")
        print(f"   {json.dumps(details, indent=2)}\n")

    def on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            self.message_count += 1

            # Parse message
            data = json.loads(msg.payload.decode())

            # Extract metrics
            temperature = data.get('cpu', {}).get('temperature_celsius')
            memory_percent = data.get('memory', {}).get('percent')
            cpu_percent = data.get('cpu', {}).get('usage_percent')

            # Store for context
            if temperature is not None:
                self.recent_temps.append(temperature)
            if memory_percent is not None:
                self.recent_memory.append(memory_percent)

            # Rule 1: Check high temperature
            if temperature is not None:
                if self.check_high_temperature(temperature):
                    alert_details = {
                        'current_temperature': temperature,
                        'threshold': self.HIGH_TEMP_THRESHOLD,
                        'duration_seconds': self.ALARM_DURATION,
                        'cpu_usage_percent': cpu_percent,
                        'recommendation': 'Check cooling system, reduce load, or shutdown to prevent damage'
                    }
                    self.publish_alert('temperature', alert_details)

            # Rule 2: Check memory exhaustion
            if memory_percent is not None:
                if self.check_memory_exhaustion(memory_percent):
                    alert_details = {
                        'current_memory_usage': memory_percent,
                        'threshold': self.HIGH_MEMORY_THRESHOLD,
                        'duration_seconds': self.ALARM_DURATION,
                        'cpu_usage_percent': cpu_percent,
                        'recommendation': 'Kill non-essential processes or add more RAM'
                    }
                    self.publish_alert('memory_exhaustion', alert_details)

            # Print status every 100 messages
            if self.message_count % 100 == 0:
                print(f"Status: {self.message_count} msgs | "
                      f"Temp: {temperature:.1f}°C | "
                      f"Memory: {memory_percent:.1f}% | "
                      f"Temp alarms: {self.temp_alarms_triggered} | "
                      f"Memory alarms: {self.memory_alarms_triggered}")

        except Exception as e:
            print(f"✗ Error processing message: {e}")

    def run(self):
        """Start monitoring for malfunctions"""
        print("=" * 70)
        print("Raspberry Pi Malfunction Detector")
        print("=" * 70)
        print(f"Broker: {self.broker}:{self.port}")
        print(f"Input topic: {self.topic_cpu}")
        print(f"Alert topic: {self.topic_alerts}")
        print("=" * 70)

        # Connect to MQTT broker
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
        except Exception as e:
            print(f"✗ Failed to connect to broker: {e}")
            return

        # Start loop
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")

        # Print summary
        print(f"\n{'='*70}")
        print("Summary")
        print(f"{'='*70}")
        print(f"Total messages processed: {self.message_count}")
        print(f"Temperature alarms: {self.temp_alarms_triggered}")
        print(f"Memory alarms: {self.memory_alarms_triggered}")
        print(f"{'='*70}\n")

        self.client.disconnect()
        print("✓ Disconnected from broker")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Monitor Raspberry Pi for malfunctions'
    )
    parser.add_argument(
        '--broker', '-b',
        default='localhost',
        help='MQTT broker IP address (default: localhost)'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=1883,
        help='MQTT broker port (default: 1883)'
    )

    args = parser.parse_args()

    # Create and run detector
    detector = MalfunctionDetector(
        broker=args.broker,
        port=args.port
    )

    detector.run()


if __name__ == '__main__':
    main()
