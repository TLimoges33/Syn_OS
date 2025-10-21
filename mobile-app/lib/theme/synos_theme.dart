// SynOS Theme - Dark cyberpunk theme with red accents

import 'package:flutter/material.dart';

class SynOSTheme {
  // Colors
  static const Color primaryRed = Color(0xFFDC143C);  // Crimson
  static const Color secondaryRed = Color(0xFFFF6B6B);
  static const Color backgroundDark = Color(0xFF0D0D0D);
  static const Color surfaceDark = Color(0xFF1A1A1A);
  static const Color cardDark = Color(0xFF2A2A2A);

  // Severity colors
  static const Color criticalRed = Color(0xFFDC143C);
  static const Color highOrange = Color(0xFFFF8C00);
  static const Color mediumYellow = Color(0xFFFFA500);
  static const Color lowGreen = Color(0xFF00FF00);
  static const Color infoBlue = Color(0xFF1E90FF);

  // Text colors
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFB0B0B0);
  static const Color textTertiary = Color(0xFF808080);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: primaryRed,
      scaffoldBackgroundColor: backgroundDark,
      cardColor: cardDark,
      dividerColor: Color(0xFF333333),

      appBarTheme: AppBarTheme(
        backgroundColor: surfaceDark,
        elevation: 0,
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
        iconTheme: IconThemeData(color: primaryRed),
      ),

      cardTheme: CardTheme(
        color: cardDark,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),

      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryRed,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        ),
      ),

      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryRed,
        ),
      ),

      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceDark,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: primaryRed, width: 2),
        ),
        labelStyle: TextStyle(color: textSecondary),
        hintStyle: TextStyle(color: textTertiary),
      ),

      iconTheme: IconThemeData(color: primaryRed),

      textTheme: TextTheme(
        displayLarge: TextStyle(color: textPrimary, fontSize: 32, fontWeight: FontWeight.bold),
        displayMedium: TextStyle(color: textPrimary, fontSize: 28, fontWeight: FontWeight.bold),
        displaySmall: TextStyle(color: textPrimary, fontSize: 24, fontWeight: FontWeight.bold),
        headlineMedium: TextStyle(color: textPrimary, fontSize: 20, fontWeight: FontWeight.w600),
        bodyLarge: TextStyle(color: textPrimary, fontSize: 16),
        bodyMedium: TextStyle(color: textSecondary, fontSize: 14),
        bodySmall: TextStyle(color: textTertiary, fontSize: 12),
      ),

      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: surfaceDark,
        selectedItemColor: primaryRed,
        unselectedItemColor: textTertiary,
        type: BottomNavigationBarType.fixed,
      ),
    );
  }

  // Helper methods for severity colors
  static Color getSeverityColor(String severity) {
    switch (severity.toLowerCase()) {
      case 'critical':
        return criticalRed;
      case 'high':
        return highOrange;
      case 'medium':
        return mediumYellow;
      case 'low':
        return lowGreen;
      case 'info':
      default:
        return infoBlue;
    }
  }

  // Helper for gradient backgrounds
  static LinearGradient get darkGradient {
    return LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        backgroundDark,
        surfaceDark,
      ],
    );
  }
}
