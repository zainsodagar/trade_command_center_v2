import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_command_center/core/network/api_client.dart';
import 'package:trade_command_center/core/services/agent_api.dart';
import 'package:trade_command_center/features/markets/data/instrument_catalog_service.dart';

void main() {
  group('InstrumentCatalogService', () {
    test('loads complete catalogue through AgentApi', () async {
      final payload = [
        _instrumentJson(
          symbol: 'EURUSD',
          group: 'Forex',
          path: r'Forex\Major\EURUSD',
        ),
        _instrumentJson(symbol: 'AAPL', group: 'Shares'),
        _instrumentJson(symbol: 'BTCUSDT', group: 'Crypto'),
      ];

      final mockHttpClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.url.path, '/api/v1/mt5/instruments');

        return http.Response(
          jsonEncode(payload),
          200,
          headers: const {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockHttpClient);

      final agentApi = AgentApi(client: apiClient);

      final service = InstrumentCatalogService(agentApi: agentApi);

      final catalog = await service.load();

      expect(catalog.totalCount, 3);

      expect(catalog.brokerGroups, ['Crypto', 'Forex', 'Shares']);

      expect(catalog.instruments.map((instrument) => instrument.brokerSymbol), [
        'EURUSD',
        'AAPL',
        'BTCUSDT',
      ]);

      service.close();
      apiClient.close();
    });

    test('preserves blocked instrument safety metadata', () async {
      final payload = [
        _instrumentJson(
          symbol: 'BTCUSD',
          group: 'RefSymbols',
          path: r'RefSymbols\BTCUSD',
          tradeMode: 'disabled',
          newOrderAllowed: false,
          referenceOnly: true,
        ),
        _instrumentJson(
          symbol: 'TONUSDT',
          group: 'Crypto',
          path: r'Crypto\TONUSDT',
          tradeMode: 'close_only',
          newOrderAllowed: false,
        ),
      ];

      final mockHttpClient = MockClient((request) async {
        return http.Response(jsonEncode(payload), 200);
      });

      final apiClient = ApiClient(client: mockHttpClient);

      final service = InstrumentCatalogService(
        agentApi: AgentApi(client: apiClient),
      );

      final catalog = await service.load();

      expect(catalog.totalCount, 2);

      expect(catalog.newOrdersAvailableCount, 0);

      expect(catalog.newOrdersBlockedCount, 2);

      expect(catalog.referenceOnlyCount, 1);

      expect(catalog.closeOnlyCount, 1);

      final btcUsd = catalog.instruments[0];

      expect(btcUsd.availabilityLabel, 'Reference only');

      final tonUsdt = catalog.instruments[1];

      expect(tonUsdt.availabilityLabel, 'Close only');

      service.close();
      apiClient.close();
    });

    test('does not hard-code broker groups', () async {
      final payload = [
        _instrumentJson(symbol: 'TEST1', group: 'FutureBrokerGroup'),
      ];

      final mockHttpClient = MockClient((request) async {
        return http.Response(jsonEncode(payload), 200);
      });

      final apiClient = ApiClient(client: mockHttpClient);

      final service = InstrumentCatalogService(
        agentApi: AgentApi(client: apiClient),
      );

      final catalog = await service.load();

      expect(catalog.brokerGroups, ['FutureBrokerGroup']);

      expect(catalog.groupCounts, {'FutureBrokerGroup': 1});

      service.close();
      apiClient.close();
    });
  });
}

Map<String, dynamic> _instrumentJson({
  required String symbol,
  required String group,
  String? path,
  String tradeMode = 'full',
  bool newOrderAllowed = true,
  bool referenceOnly = false,
}) {
  return {
    'broker_symbol': symbol,
    'broker_path': path ?? '$group\\$symbol',
    'broker_group': group,
    'description': 'Test instrument',
    'currency_base': 'USD',
    'currency_profit': 'USD',
    'currency_margin': 'USD',
    'digits': 2,
    'point': 0.01,
    'contract_size': 100.0,
    'volume_min': 0.01,
    'volume_max': 100.0,
    'volume_step': 0.01,
    'trade_mode': tradeMode,
    'trade_calc_mode': 4,
    'order_mode': 127,
    'new_order_allowed': newOrderAllowed,
    'reference_only': referenceOnly,
    'visible': false,
    'selected': false,
  };
}
