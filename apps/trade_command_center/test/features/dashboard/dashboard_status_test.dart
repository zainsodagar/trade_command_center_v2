import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/agent_status.dart';
import 'package:trade_command_center/core/models/backend_system_status.dart';
import 'package:trade_command_center/core/models/mt5_status.dart';
import 'package:trade_command_center/features/dashboard/domain/dashboard_status.dart';

void main() {
  group('DashboardStatus', () {
    test('reports operational read-only state when every layer is safe', () {
      final status = DashboardStatus(
        backend: _backend(),
        agent: _agent(),
        mt5: _mt5(),
      );

      expect(status.backendOnline, isTrue);

      expect(status.agentOnline, isTrue);

      expect(status.mt5Connected, isTrue);

      expect(status.isDemoAccount, isTrue);

      expect(status.executionEnabled, isFalse);

      expect(status.liveTradingEnabled, isFalse);

      expect(status.isReadOnlySafe, isTrue);

      expect(status.isOperationalReadOnly, isTrue);

      expect(status.accountModeLabel, 'DEMO');

      expect(status.executionLabel, 'Disabled');

      expect(status.safetyLabel, 'Read-only safe');
    });

    test('backend execution enabled makes aggregate state unsafe', () {
      final status = DashboardStatus(
        backend: _backend(executionEnabled: true),
        agent: _agent(),
        mt5: _mt5(),
      );

      expect(status.executionEnabled, isTrue);

      expect(status.isReadOnlySafe, isFalse);

      expect(status.isOperationalReadOnly, isFalse);

      expect(status.executionLabel, 'Enabled');

      expect(status.safetyLabel, 'Attention required');
    });

    test('agent live trading enabled makes aggregate state unsafe', () {
      final status = DashboardStatus(
        backend: _backend(),
        agent: _agent(liveTradingEnabled: true),
        mt5: _mt5(),
      );

      expect(status.liveTradingEnabled, isTrue);

      expect(status.isReadOnlySafe, isFalse);

      expect(status.isOperationalReadOnly, isFalse);
    });

    test('non-demo MT5 account is not operational read-only', () {
      final status = DashboardStatus(
        backend: _backend(),
        agent: _agent(),
        mt5: _mt5(accountMode: 'real'),
      );

      expect(status.isDemoAccount, isFalse);

      expect(status.accountModeLabel, 'REAL');

      expect(status.isReadOnlySafe, isTrue);

      expect(status.isOperationalReadOnly, isFalse);

      expect(status.safetyLabel, 'Attention required');
    });

    test('disconnected MT5 is not operational read-only', () {
      final status = DashboardStatus(
        backend: _backend(),
        agent: _agent(mt5Connected: false),
        mt5: _mt5(connected: false),
      );

      expect(status.mt5Connected, isFalse);

      expect(status.isOperationalReadOnly, isFalse);

      expect(status.safetyLabel, 'Attention required');
    });
  });
}

BackendSystemStatus _backend({
  bool executionEnabled = false,
  bool liveTradingEnabled = false,
}) {
  return BackendSystemStatus(
    backend: 'online',
    brokerConnections: 0,
    executionEnabled: executionEnabled,
    liveTradingEnabled: liveTradingEnabled,
  );
}

AgentStatus _agent({
  bool mt5Connected = true,
  bool executionEnabled = false,
  bool liveTradingEnabled = false,
}) {
  return AgentStatus(
    agent: 'online',
    mt5Enabled: true,
    mt5Connected: mt5Connected,
    executionEnabled: executionEnabled,
    liveTradingEnabled: liveTradingEnabled,
  );
}

Mt5Status _mt5({
  bool connected = true,
  bool executionEnabled = false,
  bool liveTradingEnabled = false,
  String? accountMode = 'demo',
}) {
  return Mt5Status(
    enabled: true,
    terminalAvailable: true,
    initialized: false,
    connected: connected,
    accountLoggedIn: true,
    executionEnabled: executionEnabled,
    liveTradingEnabled: liveTradingEnabled,
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
  );
}
