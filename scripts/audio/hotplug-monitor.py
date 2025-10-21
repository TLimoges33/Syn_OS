#!/usr/bin/env python3
"""
ALFRED Audio Device Hotplug Monitor
Automatically detects and configures new audio devices
"""

import subprocess
import time
import signal
import sys
from pathlib import Path

# Add audio manager to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "ai" / "alfred"))

try:
    from audio_manager import AudioManager, DeviceType
except ImportError:
    print("Error: Could not import AudioManager")
    print("Make sure audio_manager.py is in src/ai/alfred/")
    sys.exit(1)


class AudioHotplugMonitor:
    """Monitors for audio device hotplug events"""

    def __init__(self):
        self.audio_manager = AudioManager()
        self.known_devices = set()
        self.running = True

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down hotplug monitor...")
        self.running = False
        sys.exit(0)

    def get_device_ids(self):
        """Get set of current device IDs"""
        device_ids = set()

        for dtype in [DeviceType.SINK, DeviceType.SOURCE]:
            devices = self.audio_manager.get_devices(dtype)
            for device in devices:
                device_ids.add((device.device_type, device.name))

        return device_ids

    def on_device_added(self, device_type, device_name):
        """Handle new device connection"""
        print(f"\n🔌 Device connected: {device_name} ({device_type.value})")

        # Get device info
        devices = self.audio_manager.get_devices(device_type)
        new_device = None

        for device in devices:
            if device.name == device_name:
                new_device = device
                break

        if new_device:
            # Auto-configure based on type
            if device_type == DeviceType.SOURCE:
                # Input device - optimize for voice
                print(f"  → Configuring for voice input...")
                self.audio_manager.set_volume(new_device, 70)
                self.audio_manager.mute_device(new_device, False)

                # Optionally set as default
                print(f"  → Set as default input? [y/N] ", end="", flush=True)
                # Auto-accept for headsets
                if "headset" in device_name.lower() or "usb" in device_name.lower():
                    print("yes (auto)")
                    self.audio_manager.set_default_device(new_device)
                    print(f"  ✓ Set as default input device")
                else:
                    print("skipped")

            elif device_type == DeviceType.SINK:
                # Output device
                print(f"  → Configuring audio output...")
                self.audio_manager.set_volume(new_device, 75)
                self.audio_manager.mute_device(new_device, False)

                # Optionally set as default
                if "headset" in device_name.lower() or "usb" in device_name.lower():
                    self.audio_manager.set_default_device(new_device)
                    print(f"  ✓ Set as default output device")

    def on_device_removed(self, device_type, device_name):
        """Handle device disconnection"""
        print(f"\n🔌 Device disconnected: {device_name} ({device_type.value})")

    def monitor(self, poll_interval=2):
        """Monitor for device changes"""
        print("╔══════════════════════════════════════════════════════════╗")
        print("║   ALFRED Audio Hotplug Monitor                          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("Monitoring for audio device changes...")
        print("Press Ctrl+C to stop")
        print()

        # Get initial devices
        self.known_devices = self.get_device_ids()
        print(f"Currently tracking {len(self.known_devices)} devices")
        print()

        while self.running:
            try:
                # Check for changes
                current_devices = self.get_device_ids()

                # Detect additions
                added = current_devices - self.known_devices
                for device_type, device_name in added:
                    self.on_device_added(device_type, device_name)

                # Detect removals
                removed = self.known_devices - current_devices
                for device_type, device_name in removed:
                    self.on_device_removed(device_type, device_name)

                # Update known devices
                self.known_devices = current_devices

                # Wait before next check
                time.sleep(poll_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(poll_interval)

        print("\nMonitor stopped")


def main():
    """Main entry point"""
    monitor = AudioHotplugMonitor()
    monitor.monitor()


if __name__ == "__main__":
    main()
