import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/mt5_candle_series.dart';

void main() {
  group('Mt5CandleSeries', () {
    test('parses available fresh historical candle series', () {
      final series = Mt5CandleSeries.fromJson({
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
        'timeframe': 'M1',
        'count_requested': 2,
        'candles_available': true,
        'candle_count': 2,
        'oldest_candle_time': '2026-08-20T19:11:00Z',
        'latest_candle_time': '2026-08-20T19:12:00Z',
        'candles': [
          {
            'bar_time': '2026-08-20T19:11:00Z',
            'open': 16.9558,
            'high': 16.9565,
            'low': 16.9554,
            'close': 16.9562,
            'tick_volume': 120,
            'spread': 499,
            'real_volume': 0,
          },
          {
            'bar_time': '2026-08-20T19:12:00Z',
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
      });

      expect(series.brokerSymbol, 'USDMXN');
      expect(series.brokerGroup, 'Forex');

      expect(series.timeframe, 'M1');
      expect(series.countRequested, 2);

      expect(series.candlesAvailable, isTrue);
      expect(series.candleCount, 2);
      expect(series.candles, hasLength(2));

      expect(series.oldestCandleTime, DateTime.parse('2026-08-20T19:11:00Z'));

      expect(series.latestCandleTime, DateTime.parse('2026-08-20T19:12:00Z'));

      expect(series.candles.first.open, 16.9558);
      expect(series.candles.last.close, 16.9565);

      expect(series.selectedBefore, isTrue);
      expect(series.selectedAfter, isTrue);

      expect(series.unavailableReason, isNull);
      expect(series.errorCode, isNull);
      expect(series.errorMessage, isNull);
    });

    test('parses safe history-stale unavailable response', () {
      final series = Mt5CandleSeries.fromJson({
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
      });

      expect(series.brokerSymbol, 'GBPUSD');

      expect(series.candlesAvailable, isFalse);
      expect(series.candleCount, 0);
      expect(series.candles, isEmpty);

      expect(series.oldestCandleTime, isNull);
      expect(series.latestCandleTime, isNull);

      expect(series.unavailableReason, 'history_stale');

      expect(series.errorCode, isNull);
      expect(series.errorMessage, isNull);
    });

    test('rejects non-object candle entries', () {
      expect(
        () => Mt5CandleSeries.fromJson({
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
          'timeframe': 'M1',
          'count_requested': 1,
          'candles_available': true,
          'candle_count': 1,
          'oldest_candle_time': '2026-08-20T19:12:00Z',
          'latest_candle_time': '2026-08-20T19:12:00Z',
          'candles': ['not-an-object'],
          'unavailable_reason': null,
          'error_code': null,
          'error_message': null,
        }),
        throwsA(isA<FormatException>()),
      );
    });
  });
}
