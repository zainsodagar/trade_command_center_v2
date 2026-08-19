import 'package:flutter/material.dart';

import '../features/dashboard/domain/dashboard_status_loader.dart';
import '../features/markets/domain/instrument_catalog_loader.dart';
import '../features/shell/presentation/app_shell.dart';
import 'app_theme.dart';

class TradeCommandCenterApp extends StatelessWidget {
  const TradeCommandCenterApp({
    this.dashboardStatusLoader,
    this.instrumentCatalogLoader,
    super.key,
  });

  final DashboardStatusLoader? dashboardStatusLoader;
  final InstrumentCatalogLoader? instrumentCatalogLoader;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Trade Command Center',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.dark,
      home: AppShell(
        dashboardStatusLoader: dashboardStatusLoader,
        instrumentCatalogLoader: instrumentCatalogLoader,
      ),
    );
  }
}
