import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_command_center/core/network/api_client.dart';
import 'package:trade_command_center/core/network/api_exception.dart';
import 'package:trade_command_center/core/services/agent_api.dart';

void main() {
  group('AgentApi detailed MT5 status', () {
    test('parses operational read-only demo MT5 status', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.url.path, '/api/v1/mt5/status');

        return http.Response('''
              {
                "enabled": true,
                "terminal_available": true,
                "initialized": false,
                "connected": true,
                "account_logged_in": true,
                "execution_enabled": false,
                "live_trading_enabled": false,
                "package_version": "5.0.5735",
                "terminal_version": 500,
                "terminal_build": 6090,
                "terminal_build_date": "31 Jul 2026",
                "trade_allowed": true,
                "trade_api_disabled": false,
                "dlls_allowed": true,
                "company": "PXBT Trading Ltd",
                "terminal_name": "PXBT Trading MT5 Terminal",
                "terminal_path": "C:\\\\Program Files\\\\PXBT Trading MT5 Terminal\\\\terminal64.exe",
                "data_path": "C:\\\\Users\\\\HP\\\\AppData\\\\Roaming\\\\MetaQuotes\\\\Terminal\\\\TEST",
                "account_login_masked": "***7959",
                "account_mode": "demo",
                "account_server": "PXBTTrading-1",
                "account_company": "PXBT Trading Ltd",
                "account_currency": "USD",
                "account_leverage": 100,
                "account_trade_allowed": true,
                "account_trade_expert": true,
                "message": "MT5 terminal and demo account probe successful",
                "checked_at": "2026-08-19T18:20:00Z"
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      final status = await agentApi.getMt5Status();

      expect(status.enabled, isTrue);

      expect(status.connected, isTrue);

      expect(status.accountLoggedIn, isTrue);

      expect(status.accountLoginMasked, '***7959');

      expect(status.accountMode, 'demo');

      expect(status.accountServer, 'PXBTTrading-1');

      expect(status.accountCurrency, 'USD');

      expect(status.accountLeverage, 100);

      expect(status.executionEnabled, isFalse);

      expect(status.liveTradingEnabled, isFalse);

      expect(status.isDemoAccount, isTrue);

      expect(status.isReadOnlySafe, isTrue);

      expect(status.isOperationalReadOnly, isTrue);

      expect(status.checkedAt.toUtc(), DateTime.utc(2026, 8, 19, 18, 20));

      apiClient.close();
    });

    test('marks non-demo MT5 account as not operational read-only', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              {
                "enabled": true,
                "terminal_available": true,
                "initialized": false,
                "connected": true,
                "account_logged_in": true,
                "execution_enabled": false,
                "live_trading_enabled": false,
                "package_version": null,
                "terminal_version": null,
                "terminal_build": null,
                "terminal_build_date": null,
                "trade_allowed": null,
                "trade_api_disabled": null,
                "dlls_allowed": null,
                "company": null,
                "terminal_name": null,
                "terminal_path": null,
                "data_path": null,
                "account_login_masked": "***1234",
                "account_mode": "real",
                "account_server": null,
                "account_company": null,
                "account_currency": null,
                "account_leverage": null,
                "account_trade_allowed": null,
                "account_trade_expert": null,
                "message": "Non-demo account detected",
                "checked_at": "2026-08-19T18:20:00Z"
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      final status = await agentApi.getMt5Status();

      expect(status.isReadOnlySafe, isTrue);

      expect(status.isDemoAccount, isFalse);

      expect(status.isOperationalReadOnly, isFalse);

      apiClient.close();
    });

    test('rejects invalid detailed MT5 status schema', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              {
                "enabled": true,
                "connected": true
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      await expectLater(
        agentApi.getMt5Status(),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'MT5 status response has an invalid schema',
          ),
        ),
      );

      apiClient.close();
    });
  });
}
