import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';

class VulnerabilitiesSummaryCard extends StatelessWidget {
  final int critical, high, medium, low;

  const VulnerabilitiesSummaryCard({
    Key? key,
    required this.critical,
    required this.high,
    required this.medium,
    required this.low,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('🐛 Vulnerabilities', style: Theme.of(context).textTheme.headlineMedium),
            SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildVulnCount('Critical', critical, SynOSTheme.criticalRed),
                _buildVulnCount('High', high, SynOSTheme.highOrange),
                _buildVulnCount('Medium', medium, SynOSTheme.mediumYellow),
                _buildVulnCount('Low', low, SynOSTheme.lowGreen),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVulnCount(String label, int count, Color color) {
    return Column(
      children: [
        Text(count.toString(), style: TextStyle(fontSize: 24, color: color, fontWeight: FontWeight.bold)),
        Text(label, style: TextStyle(fontSize: 12, color: SynOSTheme.textSecondary)),
      ],
    );
  }
}
