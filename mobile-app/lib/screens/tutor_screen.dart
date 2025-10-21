// AI Tutor Screen - V1.7 Integration

import 'package:flutter/material.dart';
import '../theme/synos_theme.dart';

class TutorScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Icon(Icons.school, color: SynOSTheme.primaryRed),
            SizedBox(width: 8),
            Text('AI Tutor'),
          ],
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Learning Profile
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('🧠 Learning Profile', style: Theme.of(context).textTheme.headlineMedium),
                      SizedBox(height: 12),
                      _buildProfileRow('Style', 'Kinesthetic', Icons.touch_app),
                      _buildProfileRow('Level', '⚡ Intermediate (4.2/10)', Icons.trending_up),
                      _buildProfileRow('Success Rate', '75%', Icons.check_circle),
                      _buildProfileRow('Flow State', '🌊 Active', Icons.waves),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 16),

              // Progress
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('📊 Progress', style: Theme.of(context).textTheme.headlineMedium),
                      SizedBox(height: 12),
                      _buildProgressBar('Challenges Completed', 8, 12),
                      SizedBox(height: 8),
                      _buildProgressBar('Skills Acquired', 5, 10),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 16),

              // Recommended Challenges
              Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('🎯 Recommended Challenges', style: Theme.of(context).textTheme.headlineMedium),
                      SizedBox(height: 12),
                      _buildChallengeItem('Port Scanning Basics', 2.0, 'Scanning'),
                      _buildChallengeItem('Service Enumeration', 3.5, 'Enumeration'),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileRow(String label, String value, IconData icon) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 16, color: SynOSTheme.textSecondary),
          SizedBox(width: 8),
          Text('$label: ', style: TextStyle(color: SynOSTheme.textSecondary)),
          Text(value, style: TextStyle(color: SynOSTheme.textPrimary, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildProgressBar(String label, int current, int total) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: TextStyle(color: SynOSTheme.textSecondary, fontSize: 12)),
            Text('$current/$total', style: TextStyle(color: SynOSTheme.primaryRed, fontWeight: FontWeight.bold)),
          ],
        ),
        SizedBox(height: 4),
        LinearProgressIndicator(
          value: current / total,
          backgroundColor: SynOSTheme.surfaceDark,
          valueColor: AlwaysStoppedAnimation<Color>(SynOSTheme.primaryRed),
        ),
      ],
    );
  }

  Widget _buildChallengeItem(String title, double difficulty, String category) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: Icon(Icons.flag, color: SynOSTheme.primaryRed),
      title: Text(title),
      subtitle: Text('$category • Difficulty: ${difficulty.toStringAsFixed(1)}/10'),
      trailing: Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () {
        // TODO: Start challenge
      },
    );
  }
}
