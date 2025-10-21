// Dashboard Screen - Real-time system monitoring

import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';
import '../widgets/system_status_card.dart';
import '../widgets/active_scans_card.dart';
import '../widgets/vulnerabilities_summary_card.dart';
import '../widgets/quick_actions_card.dart';
import '../widgets/cloud_security_card.dart';

class DashboardScreen extends StatefulWidget {
  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isRefreshing = false;

  Future<void> _refreshDashboard() async {
    setState(() {
      _isRefreshing = true;
    });

    // Simulate network call
    await Future.delayed(Duration(seconds: 1));

    setState(() {
      _isRefreshing = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(Icons.security, color: SynOSTheme.primaryRed, size: 28),
            SizedBox(width: 8),
            Text('SynOS Dashboard'),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _refreshDashboard,
          ),
          IconButton(
            icon: Icon(Icons.notifications),
            onPressed: () {
              // TODO: Show notifications
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refreshDashboard,
        child: SingleChildScrollView(
          physics: AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // System Status
              SystemStatusCard(
                cpuUsage: 45.2,
                memoryUsage: 62.8,
                diskUsage: 38.5,
                networkActive: true,
                uptimeSeconds: 86400,
              ),

              // Active Scans
              ActiveScansCard(
                activeScans: [
                  {
                    'id': 'scan-001',
                    'tool': 'nmap',
                    'target': '192.168.1.0/24',
                    'progress': 0.65,
                    'eta': 300,
                  },
                  {
                    'id': 'scan-002',
                    'tool': 'nuclei',
                    'target': 'example.com',
                    'progress': 0.30,
                    'eta': 600,
                  },
                ],
              ),

              // Vulnerabilities Summary
              VulnerabilitiesSummaryCard(
                critical: 2,
                high: 5,
                medium: 12,
                low: 8,
              ),

              // Cloud Security (V1.6 integration)
              CloudSecurityCard(
                awsScore: 73,
                azureScore: 81,
                gcpScore: 68,
              ),

              // Quick Actions
              QuickActionsCard(),

              SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }
}
