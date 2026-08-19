import 'package:trade_command_center/core/models/agent_status.dart';
import 'package:trade_command_center/core/models/backend_system_status.dart';
import 'package:trade_command_center/core/models/mt5_status.dart';
import 'package:trade_command_center/features/dashboard/domain/dashboard_status.dart';
import 'package:trade_command_center/features/dashboard/domain/dashboard_status_loader.dart';

typedef DashboardLoadCallback = Future<DashboardStatus> Function();

class FakeDashboardStatusLoader implements DashboardStatusLoader {
  FakeDashboardStatusLoader({required this.onLoad});

  final DashboardLoadCallback onLoad;

  int loadCount = 0;
  bool closed = false;

  @override
  Future<DashboardStatus> load() {
    loadCount += 1;
    return onLoad();
  }

  @override
  void close() {
    closed = true;
  }
}

FakeDashboardStatusLoader buildSafeDashboardLoader() {
  return FakeDashboardStatusLoader(onLoad: () async => buildDashboardStatus());
}

DashboardStatus buildDashboardStatus({
  bool backendOnline = true,
  bool agentOnline = true,
  bool mt5Enabled = true,
  bool mt5Connected = true,
  bool accountLoggedIn = true,
  bool backendExecutionEnabled = false,
  bool backendLiveTradingEnabled = false,
  bool agentExecutionEnabled = false,
  bool agentLiveTradingEnabled = false,
  bool mt5ExecutionEnabled = false,
  bool mt5LiveTradingEnabled = false,
  String? accountMode = 'demo',
}) {
  return DashboardStatus(
    backend: BackendSystemStatus(
      backend: backendOnline ? 'online' : 'offline',
      brokerConnections: 0,
      executionEnabled: backendExecutionEnabled,
      liveTradingEnabled: backendLiveTradingEnabled,
    ),
    agent: AgentStatus(
      agent: agentOnline ? 'online' : 'offline',
      mt5Enabled: mt5Enabled,
      mt5Connected: mt5Connected,
      executionEnabled: agentExecutionEnabled,
      liveTradingEnabled: agentLiveTradingEnabled,
    ),
    mt5: Mt5Status(
      enabled: mt5Enabled,
      terminalAvailable: true,
      initialized: false,
      connected: mt5Connected,
      accountLoggedIn: accountLoggedIn,
      executionEnabled: mt5ExecutionEnabled,
      liveTradingEnabled: mt5LiveTradingEnabled,
      packageVersion: '5.0.5735',
      terminalVersion: 500,
      terminalBuild: 6090,
      terminalBuildDate: '31 Jul 2026',
      tradeAllowed: true,
      tradeApiDisabled: false,
      dllsAllowed: true,
      company: 'PXBT Trading Ltd',
      terminalName: 'PXBT Trading MT5 Terminal',
      terminalPath: null,
      dataPath: null,
      accountLoginMasked: '***7959',
      accountMode: accountMode,
      accountServer: 'PXBTTrading-1',
      accountCompany: 'PXBT Trading Ltd',
      accountCurrency: 'USD',
      accountLeverage: 100,
      accountTradeAllowed: true,
      accountTradeExpert: true,
      message: 'MT5 terminal and demo account probe successful',
      checkedAt: DateTime.utc(2026, 8, 19, 18, 30),
    ),
  );
}
