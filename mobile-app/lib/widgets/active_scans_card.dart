import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';

class ActiveScansCard extends StatelessWidget {
  final List<Map<String, dynamic>> activeScans;

  const ActiveScansCard({Key? key, required this.activeScans}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🔍 Active Scans', style: Theme.of(context).textTheme.headlineMedium),
            SizedBox(height: 12),
            ...activeScans.map((scan) => _buildScanItem(scan)).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildScanItem(Map<String, dynamic> scan) {
    return Column(
      children: [
        Row(
          children: [
            Icon(Icons.radar, size: 16, color: SynOSTheme.primaryRed),
            SizedBox(width: 8),
            Expanded(
              child: Text('${scan['tool']} → ${scan['target']}'),
            ),
          ],
        ),
        SizedBox(height: 4),
        LinearProgressIndicator(value: scan['progress']),
        SizedBox(height: 8),
      ],
    );
  }
}
