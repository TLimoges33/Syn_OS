// System Status Card Widget

import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';

class SystemStatusCard extends StatelessWidget {
  final double cpuUsage;
  final double memoryUsage;
  final double diskUsage;
  final bool networkActive;
  final int uptimeSeconds;

  const SystemStatusCard({
    Key? key,
    required this.cpuUsage,
    required this.memoryUsage,
    required this.diskUsage,
    required this.networkActive,
    required this.uptimeSeconds,
  }) : super(key: key);

  String _formatUptime(int seconds) {
    final hours = seconds ~/ 3600;
    final minutes = (seconds % 3600) ~/ 60;
    return '${hours}h ${minutes}m';
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.computer, color: SynOSTheme.primaryRed),
                SizedBox(width: 8),
                Text(
                  'System Status',
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
                Spacer(),
                Icon(
                  networkActive ? Icons.wifi : Icons.wifi_off,
                  color: networkActive ? Colors.green : Colors.red,
                ),
              ],
            ),
            SizedBox(height: 16),

            _buildMetric('CPU Usage', cpuUsage, Icons.memory),
            SizedBox(height: 12),
            _buildMetric('Memory Usage', memoryUsage, Icons.storage),
            SizedBox(height: 12),
            _buildMetric('Disk Usage', diskUsage, Icons.sd_storage),
            SizedBox(height: 16),

            Row(
              children: [
                Icon(Icons.access_time, size: 16, color: SynOSTheme.textSecondary),
                SizedBox(width: 4),
                Text(
                  'Uptime: ${_formatUptime(uptimeSeconds)}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetric(String label, double value, IconData icon) {
    Color color = value > 80 ? Colors.red : value > 60 ? Colors.orange : Colors.green;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 16, color: SynOSTheme.textSecondary),
            SizedBox(width: 4),
            Text(label, style: TextStyle(color: SynOSTheme.textSecondary, fontSize: 12)),
            Spacer(),
            Text('${value.toStringAsFixed(1)}%', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
          ],
        ),
        SizedBox(height: 4),
        LinearProgressIndicator(
          value: value / 100,
          backgroundColor: SynOSTheme.surfaceDark,
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }
}
