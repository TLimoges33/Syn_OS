import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';

class QuickActionsCard extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('⚡ Quick Actions', style: Theme.of(context).textTheme.headlineMedium),
            SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildActionChip(Icons.search, 'Scan'),
                _buildActionChip(Icons.security, 'Audit'),
                _buildActionChip(Icons.bug_report, 'Fuzz'),
                _buildActionChip(Icons.cloud, 'Cloud Check'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionChip(IconData icon, String label) {
    return ActionChip(
      avatar: Icon(icon, size: 18, color: SynOSTheme.primaryRed),
      label: Text(label),
      onPressed: () {},
    );
  }
}
