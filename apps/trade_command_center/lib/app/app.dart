import 'package:flutter/material.dart';

import '../features/shell/presentation/app_shell.dart';
import 'app_theme.dart';

class TradeCommandCenterApp extends StatelessWidget {
  const TradeCommandCenterApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Trade Command Center',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dark,
      home: const AppShell(),
    );
  }
}
