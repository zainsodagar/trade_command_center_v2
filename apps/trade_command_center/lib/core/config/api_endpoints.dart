abstract final class ApiEndpoints {
  // Backend system endpoints.
  static const String backendHealth = '/health';
  static const String systemStatus = '/api/v1/system/status';

  // Windows execution-agent system endpoints.
  static const String agentHealth = '/health';
  static const String agentStatus = '/api/v1/agent/status';

  // PrimeXBT MT5 read-only endpoints.
  static const String mt5Status = '/api/v1/mt5/status';
  static const String mt5Instruments = '/api/v1/mt5/instruments';
  static const String mt5Quote = '/api/v1/mt5/quote';
  static const String mt5Candles = '/api/v1/mt5/candles';
  static const String mt5Account = '/api/v1/mt5/account';
}
