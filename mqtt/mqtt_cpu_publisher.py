"""
MQTT Program 1: CPU Performance Publisher
==========================================

Publishes CPU performance data using paho-mqtt and psutil.
Publishes readings every 10ms (if possible) during Bayesian model operation.

Assignment: Part 1 - Data Stream Management System (15%)

Usage:
    python3 mqtt_cpu_publisher.py [--broker BROKER_IP] [--interval MS]
"""

import paho.mqtt.client as mqtt
import psutil
import json
import time
import argparse
from datetime import datetime
import sys


class CPUPerformancePublisher:
    """
    Publishes CPU performance metrics via MQTT

    Metrics Published:
    - CPU usage percentage (overall and per-core)
    - CPU frequency (current, min, max)
    - CPU temperature (if available)
    - Memory usage (total, available, percent)
    - System load average
    - Process count
    - Timestamp (ISO format)
    """

    def __init__(self, broker='localhost', port=1883, interval_ms=10):
        """
        Initialize CPU performance publisher

        Args:
            broker: MQTT broker IP address
            port: MQTT broker port (default 1883)
            interval_ms: Publishing interval in milliseconds
        """
        self.broker = broker
        self.port = port
        self.interval = interval_ms / 1000.0  # Convert to seconds

        # MQTT topics
        self.topic_base = "dataFusion/cpu"
        self.topic_performance = f"{self.topic_base}/performance"
        self.topic_status = f"{self.topic_base}/status"

        # MQTT client
        self.client = mqtt.Client(client_id="cpu_publisher")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        self.connected = False
        self.message_count = 0

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            print(f"✓ Connected to MQTT broker at {self.broker}:{self.port}")

            # Publish status message
            status_msg = {
                'status': 'online',
                'timestamp': datetime.utcnow().isoformat(),
                'interval_ms': self.interval * 1000,
                'publisher': 'cpu_performance'
            }
            client.publish(self.topic_status, json.dumps(status_msg), qos=1, retain=True)
        else:
            print(f"✗ Connection failed with code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            print(f"⚠ Unexpected disconnection. Code: {rc}")

    def get_cpu_temperature(self):
        """
        Get CPU temperature (Raspberry Pi specific)
        Returns None if not available
        """
        try:
            # Try Raspberry Pi method
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return round(temp, 2)
        except:
            # Try psutil sensors (if available)
            try:
                temps = psutil.sensors_temperatures()
                if 'cpu-thermal' in temps:
                    return round(temps['cpu-thermal'][0].current, 2)
                elif 'coretemp' in temps:
                    return round(temps['coretemp'][0].current, 2)
            except:
                pass
        return None

    def collect_performance_metrics(self):
        """
        Collect CPU and system performance metrics

        Returns:
            dict: Performance metrics with timestamp
        """
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.01, percpu=False)
        cpu_percent_per_core = psutil.cpu_percent(interval=0.01, percpu=True)

        # CPU frequency
        cpu_freq = psutil.cpu_freq()

        # Memory metrics
        memory = psutil.virtual_memory()

        # Load average (Unix only)
        try:
            load_avg = psutil.getloadavg()
        except:
            load_avg = None

        # Process count
        process_count = len(psutil.pids())

        # CPU temperature
        temperature = self.get_cpu_temperature()

        # Construct message
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': self.message_count,
            'cpu': {
                'usage_percent': round(cpu_percent, 2),
                'usage_per_core': [round(x, 2) for x in cpu_percent_per_core],
                'core_count': psutil.cpu_count(logical=False),
                'thread_count': psutil.cpu_count(logical=True),
            },
            'memory': {
                'total_mb': round(memory.total / (1024**2), 2),
                'available_mb': round(memory.available / (1024**2), 2),
                'used_mb': round(memory.used / (1024**2), 2),
                'percent': round(memory.percent, 2)
            },
            'system': {
                'process_count': process_count,
            }
        }

        # Add frequency if available
        if cpu_freq:
            metrics['cpu']['frequency_mhz'] = {
                'current': round(cpu_freq.current, 2),
                'min': round(cpu_freq.min, 2) if cpu_freq.min else None,
                'max': round(cpu_freq.max, 2) if cpu_freq.max else None
            }

        # Add load average if available
        if load_avg:
            metrics['system']['load_avg'] = {
                '1min': round(load_avg[0], 2),
                '5min': round(load_avg[1], 2),
                '15min': round(load_avg[2], 2)
            }

        # Add temperature if available
        if temperature is not None:
            metrics['cpu']['temperature_celsius'] = temperature

        return metrics

    def publish_metrics(self):
        """Collect and publish CPU performance metrics"""
        metrics = self.collect_performance_metrics()

        # Publish to MQTT
        result = self.client.publish(
            self.topic_performance,
            json.dumps(metrics),
            qos=0  # QoS 0 for high-frequency data
        )

        self.message_count += 1

        # Print every 100 messages to avoid flooding console
        if self.message_count % 100 == 0:
            print(f"Published {self.message_count} messages | "
                  f"CPU: {metrics['cpu']['usage_percent']}% | "
                  f"Memory: {metrics['memory']['percent']}%")

        return result.is_published()

    def run(self, duration_seconds=None):
        """
        Start publishing CPU performance data

        Args:
            duration_seconds: How long to run (None = infinite)
        """
        print("=" * 70)
        print("MQTT CPU Performance Publisher")
        print("=" * 70)
        print(f"Broker: {self.broker}:{self.port}")
        print(f"Topic: {self.topic_performance}")
        print(f"Interval: {self.interval * 1000:.1f}ms")
        print(f"Duration: {'Infinite' if duration_seconds is None else f'{duration_seconds}s'}")
        print("=" * 70)

        # Connect to MQTT broker
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"✗ Failed to connect to broker: {e}")
            return

        # Wait for connection
        timeout = 10
        start = time.time()
        while not self.connected and (time.time() - start) < timeout:
            time.sleep(0.1)

        if not self.connected:
            print("✗ Connection timeout")
            return

        print("\n✓ Publishing CPU metrics (Ctrl+C to stop)...\n")

        # Publishing loop
        start_time = time.time()
        try:
            while True:
                # Check duration
                if duration_seconds is not None:
                    if (time.time() - start_time) >= duration_seconds:
                        print(f"\n✓ Duration limit reached ({duration_seconds}s)")
                        break

                # Publish metrics
                self.publish_metrics()

                # Sleep for interval
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")

        # Cleanup
        print(f"\nTotal messages published: {self.message_count}")

        # Publish offline status
        status_msg = {
            'status': 'offline',
            'timestamp': datetime.utcnow().isoformat(),
            'total_messages': self.message_count
        }
        self.client.publish(self.topic_status, json.dumps(status_msg), qos=1, retain=True)

        self.client.loop_stop()
        self.client.disconnect()
        print("✓ Disconnected from broker")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Publish CPU performance metrics via MQTT'
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
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=10,
        help='Publishing interval in milliseconds (default: 10ms)'
    )
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=None,
        help='Duration in seconds (default: infinite)'
    )

    args = parser.parse_args()

    # Create and run publisher
    publisher = CPUPerformancePublisher(
        broker=args.broker,
        port=args.port,
        interval_ms=args.interval
    )

    publisher.run(duration_seconds=args.duration)


if __name__ == '__main__':
    main()
