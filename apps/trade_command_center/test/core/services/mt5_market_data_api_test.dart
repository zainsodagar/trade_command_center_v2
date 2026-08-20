import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_command_center/core/network/api_client.dart';
import 'package:trade_command_center/core/network/api_exception.dart';
import 'package:trade_command_center/core/services/agent_api.dart';

void main() {
  group('AgentApi MT5 market data', () {
    test('gets quote with GET and exact broker symbol query', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/v1/mt5/quote');
        expect(request.url.queryParameters, {'broker_symbol': 'BTCUSDT'});

        return http.Response(
          jsonEncode(_availableQuoteJson()),
          200,
          headers: const {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockClient);
      final agentApi = AgentApi(client: apiClient);

      final quote = await agentApi.getMt5Quote('BTCUSDT');

      expect(quote.brokerSymbol, 'BTCUSDT');
      expect(quote.quoteAvailable, isTrue);
      expect(quote.bid, 72740.5);
      expect(quote.ask, 72789.4);

      apiClient.close();
    });

    test('wraps malformed quote schema in ApiException', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        return http.Response(jsonEncode({'broker_symbol': 'BTCUSDT'}), 200);
      });

      final apiClient = ApiClient(client: mockClient);
      final agentApi = AgentApi(client: apiClient);

      await expectLater(
        agentApi.getMt5Quote('BTCUSDT'),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'MT5 quote response has an invalid schema',
          ),
        ),
      );

      apiClient.close();
    });

    test('gets candles with GET and exact query parameters', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/v1/mt5/candles');
        expect(request.url.queryParameters, {
          'broker_symbol': 'USDMXN',
          'timeframe': 'M5',
          'count': '25',
        });

        return http.Response(
          jsonEncode(_availableCandleSeriesJson()),
          200,
          headers: const {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockClient);
      final agentApi = AgentApi(client: apiClient);

      final series = await agentApi.getMt5Candles(
        brokerSymbol: 'USDMXN',
        timeframe: 'M5',
        count: 25,
      );

      expect(series.brokerSymbol, 'USDMXN');
      expect(series.timeframe, 'M5');
      expect(series.countRequested, 25);

      expect(series.candlesAvailable, isTrue);
      expect(series.candleCount, 2);
      expect(series.candles, hasLength(2));

      apiClient.close();
    });

    test('preserves safe history-stale response', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');
        expect(request.url.path, '/api/v1/mt5/candles');

        return http.Response(
          jsonEncode(_historyStaleJson()),
          200,
          headers: const {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockClient);
      final agentApi = AgentApi(client: apiClient);

      final series = await agentApi.getMt5Candles(
        brokerSymbol: 'GBPUSD',
        timeframe: 'M1',
        count: 5,
      );

      expect(series.candlesAvailable, isFalse);
      expect(series.candleCount, 0);
      expect(series.candles, isEmpty);

      expect(series.oldestCandleTime, isNull);
      expect(series.latestCandleTime, isNull);

      expect(series.unavailableReason, 'history_stale');

      apiClient.close();
    });

    test('uses safe default candle timeframe and count', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.url.queryParameters, {
          'broker_symbol': 'USDMXN',
          'timeframe': 'M1',
          'count': '100',
        });

        return http.Response(
          jsonEncode(
            _availableCandleSeriesJson(timeframe: 'M1', countRequested: 100),
          ),
          200,
        );
      });

      final apiClient = ApiClient(client: mockClient);
      final agentApi = AgentApi(client: apiClient);

      final series = await agentApi.getMt5Candles(brokerSymbol: 'USDMXN');

      expect(series.timeframe, 'M1');
      expect(series.countRequested, 100);

      apiClient.close();
    });
  });
}

Map<String, dynamic> _availableQuoteJson() {
  return {
    'broker_symbol': 'BTCUSDT',
    'broker_path': r'Crypto\BTCUSDT',
    'broker_group': 'Crypto',
    'digits': 1,
    'point': 0.1,
    'trade_mode': 'full',
    'new_order_allowed': true,
    'reference_only': false,
    'visible': true,
    'selected': true,
    'quote_available': true,
    'tick_time': '2026-08-20T17:27:34Z',
    'tick_time_msc': 1787246854847,
    'bid': 72740.5,
    'ask': 72789.4,
    'last': 0.0,
    'volume': 0,
    'volume_real': 0.0,
    'flags': 1030,
    'spread': 48.9,
    'spread_points': 489.0,
    'unavailable_reason': null,
    'error_code': null,
    'error_message': null,
  };
}

Map<String, dynamic> _availableCandleSeriesJson({
  String timeframe = 'M5',
  int countRequested = 25,
}) {
  return {
    'broker_symbol': 'USDMXN',
    'broker_path': r'Forex\Exotic\MXN\USDMXN',
    'broker_group': 'Forex',
    'digits': 5,
    'point': 0.00001,
    'trade_mode': 'full',
    'new_order_allowed': true,
    'reference_only': false,
    'visible_before': false,
    'selected_before': true,
    'visible_after': false,
    'selected_after': true,
    'timeframe': timeframe,
    'count_requested': countRequested,
    'candles_available': true,
    'candle_count': 2,
    'oldest_candle_time': '2026-08-20T19:10:00Z',
    'latest_candle_time': '2026-08-20T19:15:00Z',
    'candles': [
      {
        'bar_time': '2026-08-20T19:10:00Z',
        'open': 16.9558,
        'high': 16.9565,
        'low': 16.9554,
        'close': 16.9562,
        'tick_volume': 120,
        'spread': 499,
        'real_volume': 0,
      },
      {
        'bar_time': '2026-08-20T19:15:00Z',
        'open': 16.9562,
        'high': 16.9571,
        'low': 16.9558,
        'close': 16.9565,
        'tick_volume': 143,
        'spread': 499,
        'real_volume': 0,
      },
    ],
    'unavailable_reason': null,
    'error_code': null,
    'error_message': null,
  };
}

Map<String, dynamic> _historyStaleJson() {
  return {
    'broker_symbol': 'GBPUSD',
    'broker_path': r'Forex\Majors\GBPUSD',
    'broker_group': 'Forex',
    'digits': 5,
    'point': 0.00001,
    'trade_mode': 'full',
    'new_order_allowed': true,
    'reference_only': false,
    'visible_before': true,
    'selected_before': true,
    'visible_after': true,
    'selected_after': true,
    'timeframe': 'M1',
    'count_requested': 5,
    'candles_available': false,
    'candle_count': 0,
    'oldest_candle_time': null,
    'latest_candle_time': null,
    'candles': [],
    'unavailable_reason': 'history_stale',
    'error_code': null,
    'error_message': null,
  };
}
