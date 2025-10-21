// SynOS Mobile Companion - V1.8 "Mobile Companion"
// Flutter mobile app for remote monitoring and management

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/dashboard_screen.dart';
import 'screens/scans_screen.dart';
import 'screens/vulnerabilities_screen.dart';
import 'screens/tutor_screen.dart';
import 'screens/settings_screen.dart';
import 'services/websocket_service.dart';
import 'theme/synos_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Set preferred orientations
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);

  runApp(SynOSCompanionApp());
}

class SynOSCompanionApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SynOS Companion',
      debugShowCheckedModeBanner: false,
      theme: SynOSTheme.darkTheme,
      home: MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  @override
  _MainNavigationScreenState createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;
  final WebSocketService _wsService = WebSocketService();

  final List<Widget> _screens = [
    DashboardScreen(),
    ScansScreen(),
    VulnerabilitiesScreen(),
    TutorScreen(),
    SettingsScreen(),
  ];

  final List<BottomNavigationBarItem> _navItems = [
    BottomNavigationBarItem(
      icon: Icon(Icons.dashboard),
      label: 'Dashboard',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.radar),
      label: 'Scans',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.bug_report),
      label: 'Vulns',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.school),
      label: 'Tutor',
    ),
    BottomNavigationBarItem(
      icon: Icon(Icons.settings),
      label: 'Settings',
    ),
  ];

  @override
  void initState() {
    super.initState();
    _connectToSynOS();
  }

  Future<void> _connectToSynOS() async {
    try {
      await _wsService.connect('ws://localhost:8080');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('✅ Connected to SynOS'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Connection failed: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  void dispose() {
    _wsService.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: _navItems,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: SynOSTheme.primaryRed,
        unselectedItemColor: Colors.grey,
        backgroundColor: SynOSTheme.backgroundDark,
      ),
    );
  }
}
