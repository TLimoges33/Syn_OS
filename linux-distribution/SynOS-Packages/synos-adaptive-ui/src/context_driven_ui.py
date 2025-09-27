#!/usr/bin/env python3
"""
SynOS Context-Driven UI Adaptation System
Dynamic interface changes based on security phases and threat levels
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import threading
import queue

import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SecurityPhase(Enum):
    PEACE_TIME = "peace_time"
    RECONNAISSANCE = "reconnaissance"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    INCIDENT_RESPONSE = "incident_response"
    FORENSICS = "forensics"
    REPORTING = "reporting"
    MAINTENANCE = "maintenance"


class ThreatLevel(Enum):
    GREEN = 0      # Normal operations
    YELLOW = 1     # Elevated awareness
    ORANGE = 2     # High threat activity
    RED = 3        # Critical threat/active incident


class InterfaceMode(Enum):
    DESKTOP = "desktop"
    TERMINAL = "terminal"
    WEB_DASHBOARD = "web_dashboard"
    MOBILE = "mobile"
    HEADS_UP_DISPLAY = "hud"


class AccessibilityProfile(Enum):
    STANDARD = "standard"
    HIGH_CONTRAST = "high_contrast"
    LARGE_TEXT = "large_text"
    SCREEN_READER = "screen_reader"
    REDUCED_MOTION = "reduced_motion"
    KEYBOARD_ONLY = "keyboard_only"


@dataclass
class UIContext:
    security_phase: SecurityPhase
    threat_level: ThreatLevel
    interface_mode: InterfaceMode
    accessibility_profile: AccessibilityProfile
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    system_resources: Dict[str, float] = field(default_factory=dict)
    active_tools: List[str] = field(default_factory=list)
    recent_alerts: List[Dict[str, Any]] = field(default_factory=list)
    time_pressure: float = 0.0  # 0.0 = no pressure, 1.0 = maximum urgency
    cognitive_load: float = 0.0  # 0.0 = minimal, 1.0 = maximum
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UILayoutConfig:
    layout_id: str
    name: str
    description: str
    applicable_phases: List[SecurityPhase]
    threat_levels: List[ThreatLevel]
    interface_modes: List[InterfaceMode]
    layout_data: Dict[str, Any]
    priority_score: float = 0.0


@dataclass
class UIComponent:
    component_id: str
    name: str
    component_type: str
    visibility: bool = True
    position: Dict[str, Union[int, str]] = field(default_factory=dict)
    size: Dict[str, Union[int, str]] = field(default_factory=dict)
    styling: Dict[str, Any] = field(default_factory=dict)
    content: Any = None
    priority: int = 50
    accessibility_features: Dict[str, bool] = field(default_factory=dict)


class SystemMonitor:
    """Monitor system state for UI adaptation"""

    def __init__(self):
        self.current_phase = SecurityPhase.PEACE_TIME
        self.threat_level = ThreatLevel.GREEN
        self.active_tools = set()
        self.recent_alerts = []
        self.system_resources = {}

        self.monitoring = False
        self.update_interval = 5.0  # seconds

        # Event handlers
        self.phase_change_handlers: List[Callable] = []
        self.threat_level_handlers: List[Callable] = []

    def start_monitoring(self):
        """Start system monitoring"""
        self.monitoring = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()
        logging.info("System monitoring started")

    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Update system resources
                self._update_system_resources()

                # Detect active security tools
                self._detect_active_tools()

                # Check for phase changes
                new_phase = self._detect_security_phase()
                if new_phase != self.current_phase:
                    old_phase = self.current_phase
                    self.current_phase = new_phase
                    self._notify_phase_change(old_phase, new_phase)

                # Check for threat level changes
                new_threat_level = self._assess_threat_level()
                if new_threat_level != self.threat_level:
                    old_level = self.threat_level
                    self.threat_level = new_threat_level
                    self._notify_threat_level_change(old_level, new_threat_level)

                time.sleep(self.update_interval)

            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                time.sleep(self.update_interval)

    def _update_system_resources(self):
        """Update system resource information"""
        try:
            self.system_resources = {
                'cpu_percent': psutil.cpu_percent(interval=None),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_connections': len(psutil.net_connections()),
                'active_processes': len(psutil.pids())
            }
        except Exception as e:
            logging.debug(f"Failed to update system resources: {e}")

    def _detect_active_tools(self):
        """Detect active security tools"""
        security_processes = [
            'nmap', 'metasploit', 'burpsuite', 'wireshark', 'sqlmap',
            'synos-security', 'synos-reconnaissance', 'synos-vuln-scanner'
        ]

        current_tools = set()

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    for tool in security_processes:
                        if tool in proc_name:
                            current_tools.add(tool)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            logging.debug(f"Failed to detect active tools: {e}")

        self.active_tools = current_tools

    def _detect_security_phase(self) -> SecurityPhase:
        """Detect current security phase based on active tools and system state"""

        # Check for specific tool combinations
        if 'nmap' in self.active_tools or 'synos-reconnaissance' in self.active_tools:
            return SecurityPhase.RECONNAISSANCE

        if 'synos-vuln-scanner' in self.active_tools:
            return SecurityPhase.VULNERABILITY_ASSESSMENT

        if 'metasploit' in self.active_tools or 'sqlmap' in self.active_tools:
            return SecurityPhase.EXPLOITATION

        if any(tool in ['wireshark', 'volatility'] for tool in self.active_tools):
            return SecurityPhase.FORENSICS

        # Check for incident response indicators
        if self.threat_level in [ThreatLevel.ORANGE, ThreatLevel.RED]:
            return SecurityPhase.INCIDENT_RESPONSE

        # Check for high system activity (might indicate ongoing assessment)
        if (self.system_resources.get('cpu_percent', 0) > 80 or
            self.system_resources.get('network_connections', 0) > 100):
            return SecurityPhase.VULNERABILITY_ASSESSMENT

        return SecurityPhase.PEACE_TIME

    def _assess_threat_level(self) -> ThreatLevel:
        """Assess current threat level"""

        # Check recent alerts
        if self.recent_alerts:
            recent_critical = sum(1 for alert in self.recent_alerts[-10:]
                                if alert.get('severity') == 'critical')
            recent_high = sum(1 for alert in self.recent_alerts[-20:]
                            if alert.get('severity') == 'high')

            if recent_critical >= 3:
                return ThreatLevel.RED
            elif recent_critical >= 1 or recent_high >= 5:
                return ThreatLevel.ORANGE
            elif recent_high >= 2:
                return ThreatLevel.YELLOW

        # Check system indicators
        cpu_load = self.system_resources.get('cpu_percent', 0)
        network_connections = self.system_resources.get('network_connections', 0)

        if cpu_load > 95 and network_connections > 200:
            return ThreatLevel.ORANGE
        elif cpu_load > 80 or network_connections > 150:
            return ThreatLevel.YELLOW

        return ThreatLevel.GREEN

    def add_alert(self, alert: Dict[str, Any]):
        """Add security alert to monitoring"""
        alert['timestamp'] = datetime.now()
        self.recent_alerts.append(alert)

        # Keep only recent alerts (last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        self.recent_alerts = [
            alert for alert in self.recent_alerts
            if alert['timestamp'] > cutoff
        ]

    def register_phase_change_handler(self, handler: Callable):
        """Register handler for phase changes"""
        self.phase_change_handlers.append(handler)

    def register_threat_level_handler(self, handler: Callable):
        """Register handler for threat level changes"""
        self.threat_level_handlers.append(handler)

    def _notify_phase_change(self, old_phase: SecurityPhase, new_phase: SecurityPhase):
        """Notify handlers of phase change"""
        for handler in self.phase_change_handlers:
            try:
                handler(old_phase, new_phase)
            except Exception as e:
                logging.error(f"Phase change handler error: {e}")

    def _notify_threat_level_change(self, old_level: ThreatLevel, new_level: ThreatLevel):
        """Notify handlers of threat level change"""
        for handler in self.threat_level_handlers:
            try:
                handler(old_level, new_level)
            except Exception as e:
                logging.error(f"Threat level handler error: {e}")

    def get_current_context(self) -> Dict[str, Any]:
        """Get current system context"""
        return {
            'security_phase': self.current_phase.value,
            'threat_level': self.threat_level.value,
            'active_tools': list(self.active_tools),
            'system_resources': self.system_resources.copy(),
            'recent_alerts_count': len(self.recent_alerts),
            'timestamp': datetime.now().isoformat()
        }


class UILayoutManager:
    """Manage different UI layouts based on context"""

    def __init__(self):
        self.layouts: Dict[str, UILayoutConfig] = {}
        self.current_layout: Optional[UILayoutConfig] = None
        self.default_layouts = self._create_default_layouts()

        # Load default layouts
        for layout in self.default_layouts:
            self.layouts[layout.layout_id] = layout

    def _create_default_layouts(self) -> List[UILayoutConfig]:
        """Create default UI layouts for different contexts"""

        layouts = []

        # Peace time layout - Standard desktop
        peace_layout = UILayoutConfig(
            layout_id="peace_time_desktop",
            name="Standard Desktop",
            description="Normal operations desktop layout",
            applicable_phases=[SecurityPhase.PEACE_TIME, SecurityPhase.MAINTENANCE],
            threat_levels=[ThreatLevel.GREEN],
            interface_modes=[InterfaceMode.DESKTOP],
            layout_data={
                "panels": {
                    "taskbar": {"position": "bottom", "height": "40px", "visible": True},
                    "system_tray": {"position": "top-right", "visible": True},
                    "desktop": {"wallpaper": "/usr/share/synos/wallpapers/default.jpg"}
                },
                "widgets": [
                    {"type": "clock", "position": "top-right"},
                    {"type": "system_monitor", "position": "top-left", "size": "small"},
                    {"type": "security_status", "position": "bottom-right", "size": "compact"}
                ]
            }
        )
        layouts.append(peace_layout)

        # Reconnaissance layout - Tool-focused
        recon_layout = UILayoutConfig(
            layout_id="reconnaissance_focused",
            name="Reconnaissance Interface",
            description="Optimized for information gathering phase",
            applicable_phases=[SecurityPhase.RECONNAISSANCE],
            threat_levels=[ThreatLevel.GREEN, ThreatLevel.YELLOW],
            interface_modes=[InterfaceMode.DESKTOP, InterfaceMode.TERMINAL],
            layout_data={
                "panels": {
                    "tool_panel": {"position": "left", "width": "200px", "visible": True},
                    "results_panel": {"position": "center", "visible": True},
                    "notes_panel": {"position": "right", "width": "300px", "visible": True}
                },
                "tools": [
                    {"name": "nmap", "shortcut": "F1", "priority": 1},
                    {"name": "synos-security recon", "shortcut": "F2", "priority": 2},
                    {"name": "shodan", "shortcut": "F3", "priority": 3}
                ],
                "color_scheme": {
                    "primary": "#2E8B57",  # Sea green
                    "background": "#1E1E1E",
                    "text": "#FFFFFF"
                }
            }
        )
        layouts.append(recon_layout)

        # Vulnerability assessment layout
        vuln_layout = UILayoutConfig(
            layout_id="vulnerability_assessment",
            name="Vulnerability Assessment",
            description="Focused on vulnerability scanning and analysis",
            applicable_phases=[SecurityPhase.VULNERABILITY_ASSESSMENT],
            threat_levels=[ThreatLevel.GREEN, ThreatLevel.YELLOW],
            interface_modes=[InterfaceMode.DESKTOP, InterfaceMode.WEB_DASHBOARD],
            layout_data={
                "panels": {
                    "scan_control": {"position": "top", "height": "100px", "visible": True},
                    "results_grid": {"position": "center", "visible": True},
                    "vulnerability_details": {"position": "bottom", "height": "200px", "visible": True}
                },
                "widgets": [
                    {"type": "scan_progress", "position": "top-center"},
                    {"type": "vulnerability_counter", "position": "top-right"},
                    {"type": "risk_matrix", "position": "bottom-left"}
                ],
                "color_scheme": {
                    "primary": "#FF8C00",  # Dark orange
                    "background": "#1A1A1A",
                    "accent": "#FFA500"
                }
            }
        )
        layouts.append(vuln_layout)

        # Incident response layout - High urgency
        incident_layout = UILayoutConfig(
            layout_id="incident_response_war_mode",
            name="Incident Response (War Mode)",
            description="Critical incident response interface",
            applicable_phases=[SecurityPhase.INCIDENT_RESPONSE],
            threat_levels=[ThreatLevel.ORANGE, ThreatLevel.RED],
            interface_modes=[InterfaceMode.DESKTOP, InterfaceMode.HEADS_UP_DISPLAY],
            layout_data={
                "panels": {
                    "alert_banner": {"position": "top", "height": "60px", "visible": True, "priority": 1},
                    "command_center": {"position": "center", "visible": True},
                    "timeline": {"position": "left", "width": "250px", "visible": True},
                    "communication": {"position": "right", "width": "300px", "visible": True}
                },
                "alerts": {
                    "sound_enabled": True,
                    "visual_alerts": True,
                    "priority_escalation": True
                },
                "color_scheme": {
                    "primary": "#DC143C",  # Crimson
                    "background": "#000000",
                    "accent": "#FF0000",
                    "warning": "#FFFF00"
                },
                "urgency_indicators": {
                    "flash_critical": True,
                    "countdown_timers": True,
                    "progress_bars": True
                }
            }
        )
        layouts.append(incident_layout)

        # Terminal-focused layout for exploitation
        exploitation_layout = UILayoutConfig(
            layout_id="exploitation_terminal",
            name="Exploitation Terminal",
            description="Terminal-focused interface for exploitation phase",
            applicable_phases=[SecurityPhase.EXPLOITATION, SecurityPhase.POST_EXPLOITATION],
            threat_levels=[ThreatLevel.YELLOW, ThreatLevel.ORANGE],
            interface_modes=[InterfaceMode.TERMINAL],
            layout_data={
                "terminal": {
                    "split_mode": "vertical",
                    "panes": [
                        {"name": "metasploit", "command": "msfconsole", "size": "70%"},
                        {"name": "notes", "command": "vim /tmp/exploitation_notes.txt", "size": "30%"}
                    ],
                    "color_scheme": "matrix_green"
                },
                "shortcuts": {
                    "F1": "show exploits",
                    "F2": "sessions -l",
                    "F3": "use auxiliary/scanner/",
                    "F4": "search type:exploit platform:linux"
                }
            }
        )
        layouts.append(exploitation_layout)

        return layouts

    def select_optimal_layout(self, context: UIContext) -> Optional[UILayoutConfig]:
        """Select optimal layout based on current context"""

        scored_layouts = []

        for layout in self.layouts.values():
            score = self._score_layout_compatibility(layout, context)
            if score > 0:
                layout.priority_score = score
                scored_layouts.append(layout)

        if not scored_layouts:
            return None

        # Sort by score and return best match
        scored_layouts.sort(key=lambda x: x.priority_score, reverse=True)
        return scored_layouts[0]

    def _score_layout_compatibility(self, layout: UILayoutConfig, context: UIContext) -> float:
        """Score how well a layout matches the current context"""

        score = 0.0

        # Phase compatibility (high weight)
        if context.security_phase in layout.applicable_phases:
            score += 40.0

        # Threat level compatibility
        if context.threat_level in layout.threat_levels:
            score += 30.0

        # Interface mode compatibility
        if context.interface_mode in layout.interface_modes:
            score += 20.0

        # Time pressure adjustment
        if context.time_pressure > 0.7:
            # Prefer layouts designed for high urgency
            if any(phase in layout.applicable_phases
                   for phase in [SecurityPhase.INCIDENT_RESPONSE]):
                score += 15.0

        # System resource considerations
        cpu_usage = context.system_resources.get('cpu_percent', 0)
        if cpu_usage > 80:
            # Prefer lighter layouts
            if 'lightweight' in layout.layout_data.get('performance_profile', ''):
                score += 10.0

        # Accessibility profile adjustments
        if context.accessibility_profile != AccessibilityProfile.STANDARD:
            accessibility_features = layout.layout_data.get('accessibility', {})
            if context.accessibility_profile.value in accessibility_features:
                score += 10.0

        return score

    def get_layout(self, layout_id: str) -> Optional[UILayoutConfig]:
        """Get specific layout by ID"""
        return self.layouts.get(layout_id)

    def add_custom_layout(self, layout: UILayoutConfig):
        """Add custom layout configuration"""
        self.layouts[layout.layout_id] = layout


class AccessibilityAdapter:
    """Adapt UI for different accessibility needs"""

    def __init__(self):
        self.accessibility_rules = self._create_accessibility_rules()

    def _create_accessibility_rules(self) -> Dict[AccessibilityProfile, Dict[str, Any]]:
        """Create accessibility adaptation rules"""

        return {
            AccessibilityProfile.HIGH_CONTRAST: {
                'color_adjustments': {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'accent': '#FFFF00',
                    'contrast_ratio': 7.0
                },
                'ui_adjustments': {
                    'border_width': '2px',
                    'focus_indicators': True,
                    'button_styling': 'high_contrast'
                }
            },
            AccessibilityProfile.LARGE_TEXT: {
                'font_adjustments': {
                    'base_font_size': '16px',
                    'scaling_factor': 1.5,
                    'line_height': 1.6,
                    'font_weight': 'bold'
                },
                'ui_adjustments': {
                    'button_size': 'large',
                    'spacing': 'expanded',
                    'icon_size': 'large'
                }
            },
            AccessibilityProfile.SCREEN_READER: {
                'semantic_enhancements': {
                    'aria_labels': True,
                    'role_attributes': True,
                    'landmark_navigation': True,
                    'heading_structure': True
                },
                'interaction_adjustments': {
                    'keyboard_navigation': True,
                    'skip_links': True,
                    'focus_management': True
                }
            },
            AccessibilityProfile.REDUCED_MOTION: {
                'animation_adjustments': {
                    'disable_animations': True,
                    'reduce_motion': True,
                    'static_backgrounds': True,
                    'instant_transitions': True
                }
            },
            AccessibilityProfile.KEYBOARD_ONLY: {
                'interaction_adjustments': {
                    'keyboard_shortcuts': True,
                    'tab_navigation': True,
                    'focus_indicators': 'enhanced',
                    'mouse_alternatives': True
                }
            }
        }

    def apply_accessibility_adaptations(self, layout_data: Dict[str, Any],
                                      profile: AccessibilityProfile) -> Dict[str, Any]:
        """Apply accessibility adaptations to layout data"""

        if profile == AccessibilityProfile.STANDARD:
            return layout_data

        adapted_layout = layout_data.copy()
        rules = self.accessibility_rules.get(profile, {})

        # Apply color adjustments
        if 'color_adjustments' in rules:
            color_rules = rules['color_adjustments']
            if 'color_scheme' in adapted_layout:
                adapted_layout['color_scheme'].update(color_rules)

        # Apply font adjustments
        if 'font_adjustments' in rules:
            font_rules = rules['font_adjustments']
            adapted_layout['typography'] = adapted_layout.get('typography', {})
            adapted_layout['typography'].update(font_rules)

        # Apply UI adjustments
        if 'ui_adjustments' in rules:
            ui_rules = rules['ui_adjustments']
            adapted_layout['ui_settings'] = adapted_layout.get('ui_settings', {})
            adapted_layout['ui_settings'].update(ui_rules)

        # Apply animation adjustments
        if 'animation_adjustments' in rules:
            animation_rules = rules['animation_adjustments']
            adapted_layout['animations'] = adapted_layout.get('animations', {})
            adapted_layout['animations'].update(animation_rules)

        # Apply interaction adjustments
        if 'interaction_adjustments' in rules:
            interaction_rules = rules['interaction_adjustments']
            adapted_layout['interactions'] = adapted_layout.get('interactions', {})
            adapted_layout['interactions'].update(interaction_rules)

        return adapted_layout


class ContextDrivenUI:
    """Main context-driven UI adaptation system"""

    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.layout_manager = UILayoutManager()
        self.accessibility_adapter = AccessibilityAdapter()

        self.current_context: Optional[UIContext] = None
        self.current_layout: Optional[UILayoutConfig] = None

        # User preferences
        self.user_preferences = {
            'interface_mode': InterfaceMode.DESKTOP,
            'accessibility_profile': AccessibilityProfile.STANDARD,
            'theme_preference': 'auto',  # auto, light, dark
            'animation_preference': 'normal',  # none, reduced, normal, enhanced
            'notification_level': 'normal'  # minimal, normal, verbose
        }

        # Event handlers
        self.layout_change_handlers: List[Callable] = []

        # Setup event handling
        self.system_monitor.register_phase_change_handler(self._handle_phase_change)
        self.system_monitor.register_threat_level_handler(self._handle_threat_level_change)

    def start(self):
        """Start the context-driven UI system"""
        self.system_monitor.start_monitoring()
        self._update_ui_context()
        logging.info("Context-driven UI system started")

    def stop(self):
        """Stop the context-driven UI system"""
        self.system_monitor.stop_monitoring()

    def _update_ui_context(self):
        """Update current UI context"""

        system_context = self.system_monitor.get_current_context()

        # Calculate time pressure based on threat level and phase
        time_pressure = 0.0
        if system_context['threat_level'] == ThreatLevel.RED.value:
            time_pressure = 1.0
        elif system_context['threat_level'] == ThreatLevel.ORANGE.value:
            time_pressure = 0.7
        elif system_context['security_phase'] == SecurityPhase.INCIDENT_RESPONSE.value:
            time_pressure = 0.8

        # Calculate cognitive load based on active tools and alerts
        cognitive_load = min(
            len(system_context['active_tools']) * 0.1 +
            system_context['recent_alerts_count'] * 0.05,
            1.0
        )

        self.current_context = UIContext(
            security_phase=SecurityPhase(system_context['security_phase']),
            threat_level=ThreatLevel(system_context['threat_level']),
            interface_mode=self.user_preferences['interface_mode'],
            accessibility_profile=self.user_preferences['accessibility_profile'],
            user_preferences=self.user_preferences.copy(),
            system_resources=system_context['system_resources'],
            active_tools=system_context['active_tools'],
            recent_alerts=[],  # Would be populated from alert system
            time_pressure=time_pressure,
            cognitive_load=cognitive_load
        )

        # Update layout if needed
        self._update_layout()

    def _update_layout(self):
        """Update UI layout based on current context"""

        if not self.current_context:
            return

        # Select optimal layout
        optimal_layout = self.layout_manager.select_optimal_layout(self.current_context)

        if optimal_layout and optimal_layout != self.current_layout:
            # Apply accessibility adaptations
            adapted_layout_data = self.accessibility_adapter.apply_accessibility_adaptations(
                optimal_layout.layout_data,
                self.current_context.accessibility_profile
            )

            # Create adapted layout
            adapted_layout = UILayoutConfig(
                layout_id=optimal_layout.layout_id + "_adapted",
                name=optimal_layout.name,
                description=optimal_layout.description,
                applicable_phases=optimal_layout.applicable_phases,
                threat_levels=optimal_layout.threat_levels,
                interface_modes=optimal_layout.interface_modes,
                layout_data=adapted_layout_data
            )

            old_layout = self.current_layout
            self.current_layout = adapted_layout

            # Notify handlers
            self._notify_layout_change(old_layout, adapted_layout)

    def _handle_phase_change(self, old_phase: SecurityPhase, new_phase: SecurityPhase):
        """Handle security phase change"""
        logging.info(f"Security phase changed: {old_phase.value} -> {new_phase.value}")
        self._update_ui_context()

    def _handle_threat_level_change(self, old_level: ThreatLevel, new_level: ThreatLevel):
        """Handle threat level change"""
        logging.info(f"Threat level changed: {old_level.value} -> {new_level.value}")

        # Immediate UI adaptations for threat level changes
        if new_level == ThreatLevel.RED:
            self._activate_critical_mode()
        elif new_level == ThreatLevel.ORANGE:
            self._activate_high_alert_mode()

        self._update_ui_context()

    def _activate_critical_mode(self):
        """Activate critical threat mode UI adaptations"""
        logging.warning("Activating CRITICAL threat mode UI")

        # Immediate visual/audio alerts
        # This would integrate with desktop notification systems

        # Force high-visibility layouts
        if self.current_context:
            self.current_context.interface_mode = InterfaceMode.HEADS_UP_DISPLAY

    def _activate_high_alert_mode(self):
        """Activate high alert mode UI adaptations"""
        logging.warning("Activating HIGH ALERT mode UI")

        # Enhanced monitoring and visibility
        # Reduce non-essential UI elements

    def register_layout_change_handler(self, handler: Callable):
        """Register handler for layout changes"""
        self.layout_change_handlers.append(handler)

    def _notify_layout_change(self, old_layout: Optional[UILayoutConfig], new_layout: UILayoutConfig):
        """Notify handlers of layout change"""
        for handler in self.layout_change_handlers:
            try:
                handler(old_layout, new_layout)
            except Exception as e:
                logging.error(f"Layout change handler error: {e}")

    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        self.user_preferences.update(preferences)
        self._update_ui_context()

    def force_layout(self, layout_id: str) -> bool:
        """Force specific layout regardless of context"""
        layout = self.layout_manager.get_layout(layout_id)
        if layout:
            self.current_layout = layout
            self._notify_layout_change(None, layout)
            return True
        return False

    def get_current_context(self) -> Optional[UIContext]:
        """Get current UI context"""
        return self.current_context

    def get_current_layout(self) -> Optional[UILayoutConfig]:
        """Get current UI layout"""
        return self.current_layout

    def add_security_alert(self, alert: Dict[str, Any]):
        """Add security alert for context consideration"""
        self.system_monitor.add_alert(alert)
        self._update_ui_context()

    def export_layout_config(self, layout_id: str) -> Optional[Dict[str, Any]]:
        """Export layout configuration for external use"""
        layout = self.layout_manager.get_layout(layout_id)
        if layout:
            return {
                'layout_id': layout.layout_id,
                'name': layout.name,
                'description': layout.description,
                'layout_data': layout.layout_data,
                'accessibility_profile': self.current_context.accessibility_profile.value if self.current_context else 'standard'
            }
        return None


async def main():
    """Example usage of Context-Driven UI Adaptation"""
    logging.basicConfig(level=logging.INFO)

    ui_system = ContextDrivenUI()

    print("🎨 SynOS Context-Driven UI Adaptation System")
    print("=" * 50)

    # Register layout change handler
    def layout_change_handler(old_layout, new_layout):
        print(f"🔄 Layout changed: {old_layout.name if old_layout else 'None'} -> {new_layout.name}")
        print(f"   Description: {new_layout.description}")
        print(f"   Primary color: {new_layout.layout_data.get('color_scheme', {}).get('primary', 'default')}")

    ui_system.register_layout_change_handler(layout_change_handler)

    # Start the system
    ui_system.start()

    print("🚀 UI adaptation system started")

    # Simulate different scenarios
    test_scenarios = [
        {
            'name': 'Normal Operations',
            'action': lambda: None
        },
        {
            'name': 'Security Alert',
            'action': lambda: ui_system.add_security_alert({
                'severity': 'high',
                'message': 'Suspicious network activity detected'
            })
        },
        {
            'name': 'Critical Incident',
            'action': lambda: ui_system.add_security_alert({
                'severity': 'critical',
                'message': 'Active intrusion detected'
            })
        }
    ]

    for i, scenario in enumerate(test_scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['name']}")
        scenario['action']()

        await asyncio.sleep(2)  # Allow system to adapt

        context = ui_system.get_current_context()
        layout = ui_system.get_current_layout()

        if context and layout:
            print(f"   Security Phase: {context.security_phase.value}")
            print(f"   Threat Level: {context.threat_level.value}")
            print(f"   Time Pressure: {context.time_pressure:.1f}")
            print(f"   Current Layout: {layout.name}")

    # Show accessibility adaptation
    print(f"\n♿ Testing Accessibility Adaptations:")
    accessibility_profiles = [
        AccessibilityProfile.HIGH_CONTRAST,
        AccessibilityProfile.LARGE_TEXT,
        AccessibilityProfile.REDUCED_MOTION
    ]

    for profile in accessibility_profiles:
        ui_system.update_user_preferences({
            'accessibility_profile': profile
        })

        await asyncio.sleep(1)

        layout = ui_system.get_current_layout()
        if layout:
            print(f"   {profile.value}: {layout.name}")

            # Show specific adaptations
            layout_data = layout.layout_data
            if 'color_scheme' in layout_data:
                print(f"     Colors: {layout_data['color_scheme']}")
            if 'typography' in layout_data:
                print(f"     Typography: {layout_data['typography']}")

    print(f"\n✅ Context-driven UI adaptation system ready!")

    # Stop the system
    ui_system.stop()


if __name__ == "__main__":
    asyncio.run(main())