import 'json_reader.dart';

class BackendSystemStatus {
  const BackendSystemStatus({
    required this.backend,
    required this.brokerConnections,
    required this.executionEnabled,
    required this.liveTradingEnabled,
  });

  final String backend;
  final int brokerConnections;
  final bool executionEnabled;
  final bool liveTradingEnabled;

  bool get isOnline => backend.toLowerCase() == 'online';

  bool get isReadOnlySafe => !executionEnabled && !liveTradingEnabled;

  factory BackendSystemStatus.fromJson(Map<String, dynamic> json) {
    return BackendSystemStatus(
      backend: readRequiredJsonField<String>(json, 'backend'),
      brokerConnections: readRequiredJsonField<int>(json, 'broker_connections'),
      executionEnabled: readRequiredJsonField<bool>(json, 'execution_enabled'),
      liveTradingEnabled: readRequiredJsonField<bool>(
        json,
        'live_trading_enabled',
      ),
    );
  }
}
