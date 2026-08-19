import 'package:flutter/material.dart';

import '../../../core/widgets/metric_card.dart';
import '../../../core/widgets/page_frame.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PageFrame(
      title: 'Dashboard',
      subtitle: 'System health, broker connectivity, and safety state.',
      icon: Icons.dashboard_outlined,
      child: Wrap(
        spacing: 16,
        runSpacing: 16,
        children: [
          MetricCard(
            label: 'Backend',
            value: 'Not connected',
            icon: Icons.dns_outlined,
          ),
          MetricCard(
            label: 'MT5 Agent',
            value: 'Not connected',
            icon: Icons.hub_outlined,
          ),
          MetricCard(
            label: 'Account Mode',
            value: 'Demo',
            icon: Icons.science_outlined,
          ),
          MetricCard(
            label: 'Execution',
            value: 'Disabled',
            icon: Icons.lock_outline,
          ),
        ],
      ),
    );
  }
}
