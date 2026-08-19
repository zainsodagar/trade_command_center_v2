import 'package:flutter/material.dart';

import '../../../core/widgets/metric_card.dart';
import '../../../core/widgets/page_frame.dart';
import '../data/dashboard_status_service.dart';
import '../domain/dashboard_status.dart';
import '../domain/dashboard_status_loader.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({this.statusLoader, super.key});

  final DashboardStatusLoader? statusLoader;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  late final DashboardStatusLoader _statusLoader;
  late final bool _ownsStatusLoader;

  DashboardStatus? _status;
  Object? _error;
  bool _loading = true;

  @override
  void initState() {
    super.initState();

    _ownsStatusLoader = widget.statusLoader == null;

    _statusLoader = widget.statusLoader ?? DashboardStatusService();

    _loadStatus();
  }

  @override
  void dispose() {
    if (_ownsStatusLoader) {
      _statusLoader.close();
    }

    super.dispose();
  }

  Future<void> _loadStatus() async {
    if (mounted) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }

    try {
      final status = await _statusLoader.load();

      if (!mounted) {
        return;
      }

      setState(() {
        _status = status;
        _loading = false;
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _error = error;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Dashboard',
      subtitle: 'System health, broker connectivity, and safety state.',
      icon: Icons.dashboard_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _DashboardHeader(loading: _loading, onRefresh: _loadStatus),
          const SizedBox(height: 16),
          _buildStatusContent(context),
        ],
      ),
    );
  }

  Widget _buildStatusContent(BuildContext context) {
    final status = _status;
    final error = _error;

    if (status == null && _loading) {
      return const _DashboardStatePanel(
        icon: Icons.sync,
        title: 'Loading local services',
        message:
            'Reading the Trade Command Center backend, '
            'Windows execution agent, and PXBT MT5 demo status.',
        showProgress: true,
      );
    }

    if (status == null && error != null) {
      return _DashboardStatePanel(
        icon: Icons.cloud_off_outlined,
        title: 'Connection error',
        message:
            'Unable to read one or more local Trade Command '
            'Center services.\n\n$error',
      );
    }

    if (status == null) {
      return const _DashboardStatePanel(
        icon: Icons.info_outline,
        title: 'Status unavailable',
        message: 'No local service status is currently available.',
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (error != null) ...[
          const _DashboardStatePanel(
            icon: Icons.warning_amber_outlined,
            title: 'Refresh failed',
            message:
                'Showing the last successfully loaded status. '
                'Use Refresh to try the local services again.',
          ),
          const SizedBox(height: 16),
        ],
        _SafetyPanel(status: status),
        const SizedBox(height: 16),
        if (_loading) ...[
          const LinearProgressIndicator(),
          const SizedBox(height: 16),
        ],
        Wrap(
          spacing: 16,
          runSpacing: 16,
          children: [
            MetricCard(
              label: 'Backend',
              value: status.backendOnline ? 'Online' : 'Offline',
              icon: Icons.dns_outlined,
            ),
            MetricCard(
              label: 'MT5 Agent',
              value: status.mt5Connected ? 'Connected' : 'Disconnected',
              icon: Icons.hub_outlined,
            ),
            MetricCard(
              label: 'Account Mode',
              value: status.accountModeLabel,
              icon: Icons.science_outlined,
            ),
            MetricCard(
              label: 'Execution',
              value: status.executionLabel,
              icon: Icons.lock_outline,
            ),
          ],
        ),
        const SizedBox(height: 18),
        _ConnectionDetails(status: status),
      ],
    );
  }
}

class _DashboardHeader extends StatelessWidget {
  const _DashboardHeader({required this.loading, required this.onRefresh});

  final bool loading;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Expanded(
          child: Text(
            'Local service status',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
          ),
        ),
        FilledButton.tonalIcon(
          onPressed: loading ? null : onRefresh,
          icon: const Icon(Icons.refresh, size: 18),
          label: Text(loading ? 'Refreshing...' : 'Refresh'),
        ),
      ],
    );
  }
}

class _SafetyPanel extends StatelessWidget {
  const _SafetyPanel({required this.status});

  final DashboardStatus status;

  @override
  Widget build(BuildContext context) {
    final safe = status.isOperationalReadOnly;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF121C2D),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: safe
              ? Theme.of(context).colorScheme.primary.withValues(alpha: 0.45)
              : Theme.of(context).colorScheme.error.withValues(alpha: 0.65),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            safe ? Icons.verified_user_outlined : Icons.warning_amber_outlined,
            color: safe
                ? Theme.of(context).colorScheme.primary
                : Theme.of(context).colorScheme.error,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  safe ? 'Connected — read-only safe' : 'Attention required',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  safe
                      ? 'Backend, Windows agent, and PXBT MT5 '
                            'demo status are available. Execution '
                            'and live trading remain disabled.'
                      : 'One or more required read-only safety '
                            'conditions are not satisfied. This '
                            'Flutter client still exposes no '
                            'execution controls.',
                  style: const TextStyle(color: Colors.white60, height: 1.45),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ConnectionDetails extends StatelessWidget {
  const _ConnectionDetails({required this.status});

  final DashboardStatus status;

  @override
  Widget build(BuildContext context) {
    final mt5 = status.mt5;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF121C2D),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white10),
      ),
      child: Wrap(
        spacing: 28,
        runSpacing: 12,
        children: [
          _DetailItem(
            label: 'Login',
            value: mt5.accountLoginMasked ?? 'Unavailable',
          ),
          _DetailItem(
            label: 'Server',
            value: mt5.accountServer ?? 'Unavailable',
          ),
          _DetailItem(
            label: 'Currency',
            value: mt5.accountCurrency ?? 'Unavailable',
          ),
          _DetailItem(
            label: 'Leverage',
            value: mt5.accountLeverage == null
                ? 'Unavailable'
                : '1:${mt5.accountLeverage}',
          ),
          _DetailItem(
            label: 'Live Trading',
            value: status.liveTradingEnabled ? 'Enabled' : 'Disabled',
          ),
          _DetailItem(label: 'Safety', value: status.safetyLabel),
        ],
      ),
    );
  }
}

class _DetailItem extends StatelessWidget {
  const _DetailItem({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 145,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: Colors.white54),
          ),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _DashboardStatePanel extends StatelessWidget {
  const _DashboardStatePanel({
    required this.icon,
    required this.title,
    required this.message,
    this.showProgress = false,
  });

  final IconData icon;
  final String title;
  final String message;
  final bool showProgress;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      constraints: const BoxConstraints(minHeight: 220),
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: const Color(0xFF121C2D),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 38, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.white60, height: 1.45),
          ),
          if (showProgress) ...[
            const SizedBox(height: 22),
            const SizedBox(width: 220, child: LinearProgressIndicator()),
          ],
        ],
      ),
    );
  }
}
