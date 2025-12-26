"""
MQTT Program 3: Windowed Subscriber
====================================

Subscribes to CPU performance data and computes windowed averages.
Supports multiple instances with different averaging windows.

Assignment: Part 1 - Data Stream Management System (15%)

Usage:
    # Instance 1: 1-second window
    python3 mqtt_subscriber_windowed.py --window 1.0

    # Instance 2: 5-second window
    python3 mqtt_subscriber_windowed.py --window 5.0
"""

import paho.mqtt.client as mqtt
import json
import argparse
from datetime import datetime, timedelta
from collections import deque
import time
import numpy as np


class WindowedSubscriber:
    """
    Subscribes to CPU performance data and computes windowed averages

    Features:
    - Configurable time window for averaging
    - Real-time statistics (mean, std, min, max)
    - Support for multiple metrics
    - Automatic cleanup of old data
    """

    def __init__(self, broker='localhost', port=1883, window_seconds=1.0):
        """
        Initialize windowed subscriber

        Args:
            broker: MQTT broker IP address
            port: MQTT broker port
            window_seconds: Time window for averaging (seconds)
        """
        self.broker = broker
        self.port = port
        self.window_seconds = window_seconds
        self.window_timedelta = timedelta(seconds=window_seconds)

        # Data buffers (timestamp, value pairs)
        self.cpu_usage_buffer = deque()
        self.memory_usage_buffer = deque()
        self.temperature_buffer = deque()
        self.load_avg_buffer = deque()

        # Statistics tracking
        self.message_count = 0
        self.last_stats_time = time.time()
        self.stats_interval = 1.0  # Print stats every second

        # MQTT topics
        self.topic_cpu = "dataFusion/cpu/performance"

        # MQTT client
        client_id = f"windowed_subscriber_{int(window_seconds * 1000)}"
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            self.connected = True
            print(f"✓ Connected to MQTT broker at {self.broker}:{self.port}")
            print(f"✓ Window size: {self.window_seconds}s")

            # Subscribe to CPU performance topic
            client.subscribe(self.topic_cpu, qos=0)
            print(f"✓ Subscribed to: {self.topic_cpu}\n")
        else:
            print(f"✗ Connection failed with code {rc}")
            self.connected = False

    def on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        self.connected = False
        if rc != 0:
            print(f"⚠ Unexpected disconnection. Code: {rc}")

    def cleanup_old_data(self, buffer, current_time):
        """
        Remove data points older than the time window

        Args:
            buffer: deque of (timestamp, value) tuples
            current_time: Current datetime
        """
        cutoff_time = current_time - self.window_timedelta

        while buffer and buffer[0][0] < cutoff_time:
            buffer.popleft()

    def compute_statistics(self, buffer):
        """
        Compute statistics for buffered data

        Args:
            buffer: deque of (timestamp, value) tuples

        Returns:
            dict: Statistics (mean, std, min, max, count)
        """
        if not buffer:
            return None

        values = [value for timestamp, value in buffer]

        return {
            'count': len(values),
            'mean': round(np.mean(values), 3),
            'std': round(np.std(values), 3),
            'min': round(np.min(values), 3),
            'max': round(np.max(values), 3)
        }

    def on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            # Parse message
            data = json.loads(msg.payload.decode())
            message_time = datetime.fromisoformat(data['timestamp'])

            # Extract metrics
            cpu_usage = data['cpu']['usage_percent']
            memory_usage = data['memory']['percent']

            # Add to buffers
            self.cpu_usage_buffer.append((message_time, cpu_usage))
            self.memory_usage_buffer.append((message_time, memory_usage))

            # Add temperature if available
            if 'temperature_celsius' in data['cpu']:
                temp = data['cpu']['temperature_celsius']
                self.temperature_buffer.append((message_time, temp))

            # Add load average if available
            if 'load_avg' in data['system']:
                load = data['system']['load_avg']['1min']
                self.load_avg_buffer.append((message_time, load))

            # Clean up old data
            current_time = datetime.utcnow()
            self.cleanup_old_data(self.cpu_usage_buffer, current_time)
            self.cleanup_old_data(self.memory_usage_buffer, current_time)
            self.cleanup_old_data(self.temperature_buffer, current_time)
            self.cleanup_old_data(self.load_avg_buffer, current_time)

            self.message_count += 1

            # Print statistics periodically
            current_time_sec = time.time()
            if (current_time_sec - self.last_stats_time) >= self.stats_interval:
                self.print_statistics()
                self.last_stats_time = current_time_sec

        except Exception as e:
            print(f"✗ Error processing message: {e}")

    def print_statistics(self):
        """Print windowed statistics"""
        cpu_stats = self.compute_statistics(self.cpu_usage_buffer)
        memory_stats = self.compute_statistics(self.memory_usage_buffer)
        temp_stats = self.compute_statistics(self.temperature_buffer)
        load_stats = self.compute_statistics(self.load_avg_buffer)

        print(f"\n{'='*70}")
        print(f"Windowed Statistics (Window: {self.window_seconds}s)")
        print(f"{'='*70}")
        print(f"Messages received: {self.message_count}")
        print(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*70}")

        if cpu_stats:
            print(f"\nCPU Usage (%):")
            print(f"  Samples: {cpu_stats['count']:6d}")
            print(f"  Mean:    {cpu_stats['mean']:6.2f}%  ±{cpu_stats['std']:.2f}")
            print(f"  Range:   {cpu_stats['min']:6.2f}% - {cpu_stats['max']:.2f}%")

        if memory_stats:
            print(f"\nMemory Usage (%):")
            print(f"  Samples: {memory_stats['count']:6d}")
            print(f"  Mean:    {memory_stats['mean']:6.2f}%  ±{memory_stats['std']:.2f}")
            print(f"  Range:   {memory_stats['min']:6.2f}% - {memory_stats['max']:.2f}%")

        if temp_stats:
            print(f"\nCPU Temperature (°C):")
            print(f"  Samples: {temp_stats['count']:6d}")
            print(f"  Mean:    {temp_stats['mean']:6.2f}°C ±{temp_stats['std']:.2f}")
            print(f"  Range:   {temp_stats['min']:6.2f}°C - {temp_stats['max']:.2f}°C")

        if load_stats:
            print(f"\nLoad Average (1min):")
            print(f"  Samples: {load_stats['count']:6d}")
            print(f"  Mean:    {load_stats['mean']:6.2f}  ±{load_stats['std']:.2f}")
            print(f"  Range:   {load_stats['min']:6.2f} - {load_stats['max']:.2f}")

        print(f"{'='*70}\n")

    def run(self):
        """Start subscribing to CPU performance data"""
        print("=" * 70)
        print("MQTT Windowed Subscriber")
        print("=" * 70)
        print(f"Broker: {self.broker}:{self.port}")
        print(f"Topic: {self.topic_cpu}")
        print(f"Window: {self.window_seconds}s")
        print(f"Statistics interval: {self.stats_interval}s")
        print("=" * 70)

        # Connect to MQTT broker
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
        except Exception as e:
            print(f"✗ Failed to connect to broker: {e}")
            return

        print("\n✓ Subscribing to CPU performance data (Ctrl+C to stop)...\n")

        # Start loop
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")

        # Cleanup
        print(f"\nTotal messages received: {self.message_count}")

        # Print final statistics
        if self.message_count > 0:
            print("\nFinal Statistics:")
            self.print_statistics()

        self.client.disconnect()
        print("✓ Disconnected from broker")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Subscribe to CPU performance data with windowed averaging'
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
        '--window', '-w',
        type=float,
        required=True,
        help='Time window for averaging in seconds (e.g., 1.0, 5.0)'
    )

    args = parser.parse_args()

    # Create and run subscriber
    subscriber = WindowedSubscriber(
        broker=args.broker,
        port=args.port,
        window_seconds=args.window
    )

    subscriber.run()


if __name__ == '__main__':
    main()
