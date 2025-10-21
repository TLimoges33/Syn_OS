import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';

class CloudSecurityCard extends StatelessWidget {
  final int awsScore, azureScore, gcpScore;

  const CloudSecurityCard({
    Key? key,
    required this.awsScore,
    required this.azureScore,
    required this.gcpScore,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('☁️ Cloud Security', style: Theme.of(context).textTheme.headlineMedium),
            SizedBox(height: 12),
            _buildCloudScore('AWS', awsScore),
            SizedBox(height: 8),
            _buildCloudScore('Azure', azureScore),
            SizedBox(height: 8),
            _buildCloudScore('GCP', gcpScore),
          ],
        ),
      ),
    );
  }

  Widget _buildCloudScore(String provider, int score) {
    Color color = score >= 80 ? Colors.green : score >= 60 ? Colors.orange : Colors.red;
    return Row(
      children: [
        SizedBox(width: 60, child: Text(provider)),
        Expanded(
          child: LinearProgressIndicator(
            value: score / 100,
            backgroundColor: SynOSTheme.surfaceDark,
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
        SizedBox(width: 8),
        Text('$score', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
