#!/usr/bin/env python3
"""
ALFRED Audio Manager v1.1
Handles audio device management, hotplug, and optimization
"""

import subprocess
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Audio device types"""

    SINK = "sink"  # Output device
    SOURCE = "source"  # Input device


@dataclass
class AudioDevice:
    """Represents an audio device"""

    index: int
    name: str
    description: str
    device_type: DeviceType
    is_default: bool = False
    sample_rate: int = 44100
    channels: int = 2


class AudioManager:
    """Manages audio devices and configurations for ALFRED"""

    def __init__(self):
        self.logger = logging.getLogger("ALFRED.Audio")
        self._setup_logging()
        self.devices_cache = {}
        self.preferred_input = None
        self.preferred_output = None

    def _setup_logging(self):
        """Configure logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_devices(self, device_type: DeviceType) -> List[AudioDevice]:
        """Get list of audio devices"""
        try:
            if device_type == DeviceType.SINK:
                cmd = ["pactl", "list", "short", "sinks"]
            else:
                cmd = ["pactl", "list", "short", "sources"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            devices = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("\t")
                if len(parts) >= 2:
                    device = AudioDevice(
                        index=int(parts[0]),
                        name=parts[1],
                        description=parts[1],  # Basic, enhance later
                        device_type=device_type,
                    )
                    devices.append(device)

            return devices

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get devices: {e}")
            return []

    def get_default_device(self, device_type: DeviceType) -> Optional[AudioDevice]:
        """Get the default audio device"""
        try:
            if device_type == DeviceType.SINK:
                cmd = ["pactl", "get-default-sink"]
            else:
                cmd = ["pactl", "get-default-source"]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            default_name = result.stdout.strip()
            devices = self.get_devices(device_type)

            for device in devices:
                if device.name == default_name:
                    device.is_default = True
                    return device

            return None

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get default device: {e}")
            return None

    def set_default_device(self, device: AudioDevice) -> Tuple[bool, str]:
        """Set the default audio device"""
        try:
            if device.device_type == DeviceType.SINK:
                cmd = ["pactl", "set-default-sink", device.name]
            else:
                cmd = ["pactl", "set-default-source", device.name]

            subprocess.run(cmd, check=True, capture_output=True)

            self.logger.info(
                f"Set default {device.device_type.value}: {device.description}"
            )
            return True, "Default device updated"

        except subprocess.CalledProcessError as e:
            msg = f"Failed to set default device: {e}"
            self.logger.error(msg)
            return False, msg

    def set_volume(self, device: AudioDevice, volume_percent: int) -> Tuple[bool, str]:
        """Set device volume (0-100)"""
        try:
            volume_percent = max(0, min(100, volume_percent))

            if device.device_type == DeviceType.SINK:
                cmd = [
                    "pactl",
                    "set-sink-volume",
                    str(device.index),
                    f"{volume_percent}%",
                ]
            else:
                cmd = [
                    "pactl",
                    "set-source-volume",
                    str(device.index),
                    f"{volume_percent}%",
                ]

            subprocess.run(cmd, check=True, capture_output=True)

            self.logger.info(f"Set volume for {device.description}: {volume_percent}%")
            return True, f"Volume set to {volume_percent}%"

        except subprocess.CalledProcessError as e:
            msg = f"Failed to set volume: {e}"
            self.logger.error(msg)
            return False, msg

    def get_volume(self, device: AudioDevice) -> Optional[int]:
        """Get device volume (0-100)"""
        try:
            if device.device_type == DeviceType.SINK:
                cmd = ["pactl", "get-sink-volume", str(device.index)]
            else:
                cmd = ["pactl", "get-source-volume", str(device.index)]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Parse volume from output (e.g., "Volume: front-left: 65536 / 100%")
            match = re.search(r"(\d+)%", result.stdout)
            if match:
                return int(match.group(1))

            return None

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get volume: {e}")
            return None

    def mute_device(self, device: AudioDevice, mute: bool = True) -> Tuple[bool, str]:
        """Mute or unmute a device"""
        try:
            mute_str = "1" if mute else "0"

            if device.device_type == DeviceType.SINK:
                cmd = ["pactl", "set-sink-mute", str(device.index), mute_str]
            else:
                cmd = ["pactl", "set-source-mute", str(device.index), mute_str]

            subprocess.run(cmd, check=True, capture_output=True)

            action = "Muted" if mute else "Unmuted"
            self.logger.info(f"{action} {device.description}")
            return True, f"{action} device"

        except subprocess.CalledProcessError as e:
            msg = f"Failed to mute device: {e}"
            self.logger.error(msg)
            return False, msg

    def optimize_for_voice(self) -> Tuple[bool, str]:
        """Optimize audio settings for voice recognition"""
        self.logger.info("Optimizing audio for voice recognition...")

        try:
            # Get default input device
            input_device = self.get_default_device(DeviceType.SOURCE)
            if not input_device:
                return False, "No input device found"

            # Set optimal input volume (70% for voice)
            self.set_volume(input_device, 70)

            # Unmute input
            self.mute_device(input_device, False)

            # Get default output device
            output_device = self.get_default_device(DeviceType.SINK)
            if output_device:
                # Set moderate output volume
                self.set_volume(output_device, 75)
                self.mute_device(output_device, False)

            self.logger.info("Audio optimized for voice recognition")
            return True, "Audio optimization complete"

        except Exception as e:
            msg = f"Failed to optimize audio: {e}"
            self.logger.error(msg)
            return False, msg

    def test_microphone(self, duration: int = 3) -> Tuple[bool, str]:
        """Test microphone recording"""
        try:
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                test_file = tmp.name

            self.logger.info(f"Testing microphone for {duration} seconds...")

            # Record audio
            cmd = ["arecord", "-d", str(duration), "-f", "cd", test_file]
            subprocess.run(cmd, check=True, capture_output=True)

            # Check file size
            file_size = os.path.getsize(test_file)

            # Clean up
            os.unlink(test_file)

            if file_size > 1000:  # At least 1KB
                msg = f"Microphone test passed ({file_size} bytes recorded)"
                self.logger.info(msg)
                return True, msg
            else:
                msg = "Microphone test failed (no audio recorded)"
                self.logger.warning(msg)
                return False, msg

        except subprocess.CalledProcessError as e:
            msg = f"Microphone test failed: {e}"
            self.logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Microphone test error: {e}"
            self.logger.error(msg)
            return False, msg

    def get_status_report(self) -> str:
        """Generate audio system status report"""
        report = []
        report.append("╔══════════════════════════════════════════════════════════╗")
        report.append("║           ALFRED Audio System Status                    ║")
        report.append("╚══════════════════════════════════════════════════════════╝")
        report.append("")

        # Input devices
        report.append("🎤 Input Devices:")
        input_devices = self.get_devices(DeviceType.SOURCE)
        default_input = self.get_default_device(DeviceType.SOURCE)

        for device in input_devices:
            is_default = (
                " [DEFAULT]"
                if device.name == (default_input.name if default_input else "")
                else ""
            )
            volume = self.get_volume(device)
            volume_str = f" (Volume: {volume}%)" if volume else ""
            report.append(f"  • {device.description}{is_default}{volume_str}")

        report.append("")

        # Output devices
        report.append("🔊 Output Devices:")
        output_devices = self.get_devices(DeviceType.SINK)
        default_output = self.get_default_device(DeviceType.SINK)

        for device in output_devices:
            is_default = (
                " [DEFAULT]"
                if device.name == (default_output.name if default_output else "")
                else ""
            )
            volume = self.get_volume(device)
            volume_str = f" (Volume: {volume}%)" if volume else ""
            report.append(f"  • {device.description}{is_default}{volume_str}")

        report.append("")
        report.append("✅ Audio system operational")

        return "\n".join(report)


def main():
    """Test audio manager"""
    print("ALFRED Audio Manager v1.1 - Test Mode")
    print("=" * 60)
    print()

    manager = AudioManager()

    # Get status report
    print(manager.get_status_report())
    print()

    # Optimize for voice
    success, msg = manager.optimize_for_voice()
    print(f"Optimization: {msg}")
    print()

    # Test microphone
    print("Testing microphone (3 seconds)...")
    success, msg = manager.test_microphone(3)
    print(f"Microphone test: {msg}")


if __name__ == "__main__":
    main()
