import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_command_center/core/network/api_client.dart';
import 'package:trade_command_center/core/network/api_exception.dart';
import 'package:trade_command_center/core/services/agent_api.dart';

void main() {
  group('AgentApi MT5 instruments', () {
    test('parses complete bare-array catalogue without truncation', () async {
      final payload = List.generate(
        207,
        (index) => _instrumentJson(
          symbol: 'SYMBOL$index',
          group: index.isEven ? 'Forex' : 'Crypto',
        ),
      );

      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.url.path, '/api/v1/mt5/instruments');

        return http.Response(
          jsonEncode(payload),
          200,
          headers: const {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      final instruments = await agentApi.getMt5Instruments();

      expect(instruments.length, 207);

      expect(instruments.first.brokerSymbol, 'SYMBOL0');

      expect(instruments.last.brokerSymbol, 'SYMBOL206');

      expect(instruments.first.brokerGroup, 'Forex');

      expect(instruments[1].brokerGroup, 'Crypto');

      apiClient.close();
    });

    test('preserves reference-only and close-only safety metadata', () async {
      final payload = [
        _instrumentJson(
          symbol: 'BTCUSD',
          group: 'RefSymbols',
          path: r'RefSymbols\BTCUSD',
          description: 'Conversion only',
          tradeMode: 'disabled',
          newOrderAllowed: false,
          referenceOnly: true,
        ),
        _instrumentJson(
          symbol: 'TONUSDT',
          group: 'Crypto',
          path: r'Crypto\TONUSDT',
          description: 'Toncoin vs USDT',
          tradeMode: 'close_only',
          newOrderAllowed: false,
        ),
      ];

      final mockClient = MockClient((request) async {
        return http.Response(jsonEncode(payload), 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      final instruments = await agentApi.getMt5Instruments();

      expect(instruments.length, 2);

      final reference = instruments[0];

      expect(reference.brokerSymbol, 'BTCUSD');

      expect(reference.referenceOnly, isTrue);

      expect(reference.isDisabled, isTrue);

      expect(reference.canOpenNewOrders, isFalse);

      expect(reference.availabilityLabel, 'Reference only');

      final closeOnly = instruments[1];

      expect(closeOnly.brokerSymbol, 'TONUSDT');

      expect(closeOnly.isCloseOnly, isTrue);

      expect(closeOnly.canOpenNewOrders, isFalse);

      expect(closeOnly.availabilityLabel, 'Close only');

      apiClient.close();
    });

    test(
      'rejects object wrapper because live endpoint uses bare array',
      () async {
        final mockClient = MockClient((request) async {
          return http.Response(
            jsonEncode({
              'instruments': [_instrumentJson(symbol: 'AAPL', group: 'Shares')],
            }),
            200,
          );
        });

        final apiClient = ApiClient(client: mockClient);

        final agentApi = AgentApi(client: apiClient);

        await expectLater(
          agentApi.getMt5Instruments(),
          throwsA(
            isA<ApiException>().having(
              (error) => error.message,
              'message',
              'MT5 instruments response must be a JSON array',
            ),
          ),
        );

        apiClient.close();
      },
    );

    test('rejects malformed instrument entry', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode([
            {'broker_symbol': 'AAPL'},
          ]),
          200,
        );
      });

      final apiClient = ApiClient(client: mockClient);

      final agentApi = AgentApi(client: apiClient);

      await expectLater(
        agentApi.getMt5Instruments(),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'MT5 instruments response has an invalid schema',
          ),
        ),
      );

      apiClient.close();
    });
  });
}

Map<String, dynamic> _instrumentJson({
  required String symbol,
  required String group,
  String? path,
  String description = 'Test instrument',
  String tradeMode = 'full',
  bool newOrderAllowed = true,
  bool referenceOnly = false,
}) {
  return {
    'broker_symbol': symbol,
    'broker_path': path ?? '$group\\$symbol',
    'broker_group': group,
    'description': description,
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
