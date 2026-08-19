import 'package:flutter/material.dart';

import '../../account/presentation/account_page.dart';
import '../../dashboard/domain/dashboard_status_loader.dart';
import '../../dashboard/presentation/dashboard_page.dart';
import '../../markets/presentation/markets_page.dart';
import '../../settings/presentation/settings_page.dart';
import 'widgets/app_mark.dart';
import 'widgets/top_bar.dart';

class AppShell extends StatefulWidget {
  const AppShell({this.dashboardStatusLoader, super.key});

  final DashboardStatusLoader? dashboardStatusLoader;

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  static const double _extendedRailBreakpoint = 1200;

  int _selectedIndex = 0;

  static const _destinations = <NavigationRailDestination>[
    NavigationRailDestination(
      icon: Icon(Icons.dashboard_outlined),
      selectedIcon: Icon(Icons.dashboard),
      label: Text('Dashboard'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.candlestick_chart_outlined),
      selectedIcon: Icon(Icons.candlestick_chart),
      label: Text('Markets'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.account_balance_wallet_outlined),
      selectedIcon: Icon(Icons.account_balance_wallet),
      label: Text('Account'),
    ),
    NavigationRailDestination(
      icon: Icon(Icons.settings_outlined),
      selectedIcon: Icon(Icons.settings),
      label: Text('Settings'),
    ),
  ];

  List<Widget> get _pages => [
    DashboardPage(statusLoader: widget.dashboardStatusLoader),
    const MarketsPage(),
    const AccountPage(),
    const SettingsPage(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isExtended = constraints.maxWidth >= _extendedRailBreakpoint;

            return Row(
              children: [
                NavigationRail(
                  selectedIndex: _selectedIndex,
                  extended: isExtended,
                  labelType: isExtended
                      ? NavigationRailLabelType.none
                      : NavigationRailLabelType.all,
                  minWidth: 88,
                  minExtendedWidth: 210,
                  leading: const Padding(
                    padding: EdgeInsets.only(top: 12, bottom: 20),
                    child: AppMark(),
                  ),
                  destinations: _destinations,
                  onDestinationSelected: (index) {
                    setState(() {
                      _selectedIndex = index;
                    });
                  },
                ),
                const VerticalDivider(width: 1, thickness: 1),
                Expanded(
                  child: Column(
                    children: [
                      const TopBar(),
                      const Divider(height: 1, thickness: 1),
                      Expanded(
                        child: IndexedStack(
                          index: _selectedIndex,
                          children: _pages,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
