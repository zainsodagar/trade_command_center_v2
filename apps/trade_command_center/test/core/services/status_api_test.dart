import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_command_center/core/network/api_client.dart';
import 'package:trade_command_center/core/network/api_exception.dart';
import 'package:trade_command_center/core/services/agent_api.dart';
import 'package:trade_command_center/core/services/backend_api.dart';

void main() {
  group('BackendApi', () {
    test('parses safe read-only backend status', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.url.path, '/api/v1/system/status');

        return http.Response('''
              {
                "backend": "online",
                "broker_connections": 1,
                "execution_enabled": false,
                "live_trading_enabled": false
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final backendApi = BackendApi(client: apiClient);

      final status = await backendApi.getSystemStatus();

      expect(status.backend, 'online');

      expect(status.brokerConnections, 1);

      expect(status.isOnline, isTrue);

      expect(status.isReadOnlySafe, isTrue);

      expect(status.executionEnabled, isFalse);

      expect(status.liveTradingEnabled, isFalse);

      apiClient.close();
    });

    test('detects backend execution state as unsafe', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              {
                "backend": "online",
                "broker_connections": 1,
                "execution_enabled": true,
                "live_trading_enabled": false
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final backendApi = BackendApi(client: apiClient);

      final status = await backendApi.getSystemStatus();

      expect(status.isOnline, isTrue);

      expect(status.isReadOnlySafe, isFalse);

      expect(status.executionEnabled, isTrue);

      apiClient.close();
    });

    test('rejects invalid backend status schema', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              {
                "backend": "online"
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final backendApi = BackendApi(client: apiClient);

      await expectLater(
        backendApi.getSystemStatus(),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'Backend system status response has an invalid schema',
          ),
        ),
      );

      apiClient.close();
    });
  });

  group('AgentApi', () {
    test('parses safe connected demo agent status', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.url.path, '/api/v1/agent/status');

        return http.Response('''
              {
                "agent": "online",
                "mt5_enabled": true,
                "mt5_connected": true,
                "execution_enabled": false,
                "live_trading_enabled": false
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      final status = await agentApi.getAgentStatus();

      expect(status.agent, 'online');

      expect(status.mt5Enabled, isTrue);

      expect(status.mt5Connected, isTrue);

      expect(status.isOnline, isTrue);

      expect(status.isReadOnlySafe, isTrue);

      expect(status.executionEnabled, isFalse);

      expect(status.liveTradingEnabled, isFalse);

      apiClient.close();
    });

    test('detects live trading state as unsafe', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              {
                "agent": "online",
                "mt5_enabled": true,
                "mt5_connected": true,
                "execution_enabled": false,
                "live_trading_enabled": true
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      final status = await agentApi.getAgentStatus();

      expect(status.isOnline, isTrue);

      expect(status.isReadOnlySafe, isFalse);

      expect(status.liveTradingEnabled, isTrue);

      apiClient.close();
    });

    test('rejects invalid agent status schema', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              {
                "agent": "online",
                "mt5_enabled": true
              }
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      await expectLater(
        agentApi.getAgentStatus(),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'Agent status response has an invalid schema',
          ),
        ),
      );

      apiClient.close();
    });
  });
}
