import 'json_reader.dart';

class AgentStatus {
  const AgentStatus({
    required this.agent,
    required this.mt5Enabled,
    required this.mt5Connected,
    required this.executionEnabled,
    required this.liveTradingEnabled,
  });

  final String agent;
  final bool mt5Enabled;
  final bool mt5Connected;
  final bool executionEnabled;
  final bool liveTradingEnabled;

  bool get isOnline => agent.toLowerCase() == 'online';

  bool get isReadOnlySafe => !executionEnabled && !liveTradingEnabled;

  factory AgentStatus.fromJson(Map<String, dynamic> json) {
    return AgentStatus(
      agent: readRequiredJsonField<String>(json, 'agent'),
      mt5Enabled: readRequiredJsonField<bool>(json, 'mt5_enabled'),
      mt5Connected: readRequiredJsonField<bool>(json, 'mt5_connected'),
      executionEnabled: readRequiredJsonField<bool>(json, 'execution_enabled'),
      liveTradingEnabled: readRequiredJsonField<bool>(
        json,
        'live_trading_enabled',
      ),
    );
  }
}
