"""
MQTT Program 4: Bernoulli Sampling Subscriber
==============================================

Subscribes to CPU performance data using naive Bernoulli sampling.
Uses approximately 1/3 of data points to estimate averages.

Assignment: Part 1 - Data Stream Management System (15%)

Usage:
    python3 mqtt_subscriber_bernoulli.py [--broker BROKER_IP] [--probability 0.33]
"""

import paho.mqtt.client as mqtt
import json
import argparse
from datetime import datetime, timedelta
from collections import deque
import time
import numpy as np
import random


class BernoulliSamplingSubscriber:
    """
    Subscribes to CPU performance data using Bernoulli sampling

    Bernoulli Sampling:
    - Each message has probability p of being sampled
    - p = 1/3 ≈ 0.33 (use ~1/3 of data points)
    - Unbiased estimator: E[sample mean] = population mean
    - Reduces computational load while maintaining accuracy
    """

    def __init__(self, broker='localhost', port=1883, sampling_prob=1/3, window_seconds=5.0):
        """
        Initialize Bernoulli sampling subscriber

        Args:
            broker: MQTT broker IP address
            port: MQTT broker port
            sampling_prob: Probability of sampling each message (default: 1/3)
            window_seconds: Time window for averaging
        """
        self.broker = broker
        self.port = port
        self.sampling_prob = sampling_prob
        self.window_seconds = window_seconds
        self.window_timedelta = timedelta(seconds=window_seconds)

        # Data buffers (only sampled data)
        self.cpu_usage_buffer = deque()
        self.memory_usage_buffer = deque()
        self.temperature_buffer = deque()
        self.load_avg_buffer = deque()

        # Statistics tracking
        self.total_messages = 0
        self.sampled_messages = 0
        self.rejected_messages = 0
        self.last_stats_time = time.time()
        self.stats_interval = 1.0

        # MQTT topics
        self.topic_cpu = "dataFusion/cpu/performance"

        # MQTT client
        client_id = f"bernoulli_subscriber_{int(sampling_prob * 100)}"
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
            print(f"✓ Sampling probability: {self.sampling_prob:.3f} ({self.sampling_prob * 100:.1f}%)")
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

    def bernoulli_sample(self):
        """
        Perform Bernoulli sampling

        Returns:
            bool: True if message should be sampled
        """
        return random.random() < self.sampling_prob

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
            self.total_messages += 1

            # Bernoulli sampling: sample with probability p
            if not self.bernoulli_sample():
                self.rejected_messages += 1
                return  # Skip this message

            self.sampled_messages += 1

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

            # Print statistics periodically
            current_time_sec = time.time()
            if (current_time_sec - self.last_stats_time) >= self.stats_interval:
                self.print_statistics()
                self.last_stats_time = current_time_sec

        except Exception as e:
            print(f"✗ Error processing message: {e}")

    def print_statistics(self):
        """Print statistics for sampled data"""
        cpu_stats = self.compute_statistics(self.cpu_usage_buffer)
        memory_stats = self.compute_statistics(self.memory_usage_buffer)
        temp_stats = self.compute_statistics(self.temperature_buffer)
        load_stats = self.compute_statistics(self.load_avg_buffer)

        # Calculate sampling efficiency
        sampling_rate = (self.sampled_messages / self.total_messages * 100) if self.total_messages > 0 else 0

        print(f"\n{'='*70}")
        print(f"Bernoulli Sampling Statistics (p={self.sampling_prob:.3f}, Window: {self.window_seconds}s)")
        print(f"{'='*70}")
        print(f"Total messages:    {self.total_messages:6d}")
        print(f"Sampled:           {self.sampled_messages:6d} ({sampling_rate:.1f}%)")
        print(f"Rejected:          {self.rejected_messages:6d}")
        print(f"Expected rate:     {self.sampling_prob * 100:.1f}%")
        print(f"Timestamp:         {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'-'*70}")

        if cpu_stats:
            print(f"\nCPU Usage (%) [Based on {cpu_stats['count']} samples]:")
            print(f"  Mean:    {cpu_stats['mean']:6.2f}%  ±{cpu_stats['std']:.2f}")
            print(f"  Range:   {cpu_stats['min']:6.2f}% - {cpu_stats['max']:.2f}%")

        if memory_stats:
            print(f"\nMemory Usage (%) [Based on {memory_stats['count']} samples]:")
            print(f"  Mean:    {memory_stats['mean']:6.2f}%  ±{memory_stats['std']:.2f}")
            print(f"  Range:   {memory_stats['min']:6.2f}% - {memory_stats['max']:.2f}%")

        if temp_stats:
            print(f"\nCPU Temperature (°C) [Based on {temp_stats['count']} samples]:")
            print(f"  Mean:    {temp_stats['mean']:6.2f}°C ±{temp_stats['std']:.2f}")
            print(f"  Range:   {temp_stats['min']:6.2f}°C - {temp_stats['max']:.2f}°C")

        if load_stats:
            print(f"\nLoad Average (1min) [Based on {load_stats['count']} samples]:")
            print(f"  Mean:    {load_stats['mean']:6.2f}  ±{load_stats['std']:.2f}")
            print(f"  Range:   {load_stats['min']:6.2f} - {load_stats['max']:.2f}")

        print(f"\n💡 Note: Bernoulli sampling provides unbiased estimates using")
        print(f"   only ~{self.sampling_prob * 100:.0f}% of data (reduces computational load)")
        print(f"{'='*70}\n")

    def run(self):
        """Start subscribing to CPU performance data"""
        print("=" * 70)
        print("MQTT Bernoulli Sampling Subscriber")
        print("=" * 70)
        print(f"Broker: {self.broker}:{self.port}")
        print(f"Topic: {self.topic_cpu}")
        print(f"Sampling probability: {self.sampling_prob:.3f} (~{self.sampling_prob * 100:.1f}%)")
        print(f"Window: {self.window_seconds}s")
        print("=" * 70)

        # Connect to MQTT broker
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
        except Exception as e:
            print(f"✗ Failed to connect to broker: {e}")
            return

        print("\n✓ Subscribing with Bernoulli sampling (Ctrl+C to stop)...\n")

        # Start loop
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")

        # Cleanup
        print(f"\nTotal messages received: {self.total_messages}")
        print(f"Messages sampled: {self.sampled_messages}")
        print(f"Messages rejected: {self.rejected_messages}")
        print(f"Actual sampling rate: {(self.sampled_messages / self.total_messages * 100):.2f}%")

        # Print final statistics
        if self.sampled_messages > 0:
            print("\nFinal Statistics:")
            self.print_statistics()

        self.client.disconnect()
        print("✓ Disconnected from broker")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Subscribe to CPU performance data with Bernoulli sampling'
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
        '--probability', '--prob',
        type=float,
        default=1/3,
        help='Sampling probability (default: 0.333 = 1/3)'
    )
    parser.add_argument(
        '--window', '-w',
        type=float,
        default=5.0,
        help='Time window for averaging in seconds (default: 5.0)'
    )

    args = parser.parse_args()

    # Validate probability
    if not (0 < args.probability <= 1):
        print("✗ Sampling probability must be between 0 and 1")
        return

    # Create and run subscriber
    subscriber = BernoulliSamplingSubscriber(
        broker=args.broker,
        port=args.port,
        sampling_prob=args.probability,
        window_seconds=args.window
    )

    subscriber.run()


if __name__ == '__main__':
    main()
