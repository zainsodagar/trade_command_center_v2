import '../../../core/models/agent_status.dart';
import '../../../core/models/backend_system_status.dart';
import '../../../core/models/mt5_status.dart';

class DashboardStatus {
  const DashboardStatus({
    required this.backend,
    required this.agent,
    required this.mt5,
  });

  final BackendSystemStatus backend;
  final AgentStatus agent;
  final Mt5Status mt5;

  bool get backendOnline => backend.isOnline;

  bool get agentOnline => agent.isOnline;

  bool get mt5Connected => agent.mt5Connected && mt5.connected;

  bool get isDemoAccount => mt5.isDemoAccount;

  bool get executionEnabled =>
      backend.executionEnabled ||
      agent.executionEnabled ||
      mt5.executionEnabled;

  bool get liveTradingEnabled =>
      backend.liveTradingEnabled ||
      agent.liveTradingEnabled ||
      mt5.liveTradingEnabled;

  bool get isReadOnlySafe =>
      backend.isReadOnlySafe && agent.isReadOnlySafe && mt5.isReadOnlySafe;

  bool get isOperationalReadOnly =>
      backendOnline &&
      agentOnline &&
      mt5.isOperationalReadOnly &&
      isReadOnlySafe;

  String get accountModeLabel {
    final mode = mt5.accountMode;

    if (mode == null || mode.trim().isEmpty) {
      return 'Unavailable';
    }

    return mode.toUpperCase();
  }

  String get executionLabel => executionEnabled ? 'Enabled' : 'Disabled';

  String get safetyLabel =>
      isOperationalReadOnly ? 'Read-only safe' : 'Attention required';
}
