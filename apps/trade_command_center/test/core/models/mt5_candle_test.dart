import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/mt5_candle.dart';

void main() {
  group('Mt5Candle', () {
    test('parses valid MT5 historical candle', () {
      final candle = Mt5Candle.fromJson({
        'bar_time': '2026-08-20T19:12:00Z',
        'open': 16.9562,
        'high': 16.9571,
        'low': 16.9558,
        'close': 16.9565,
        'tick_volume': 143,
        'spread': 499,
        'real_volume': 0,
      });

      expect(candle.barTime, DateTime.parse('2026-08-20T19:12:00Z'));

      expect(candle.open, 16.9562);
      expect(candle.high, 16.9571);
      expect(candle.low, 16.9558);
      expect(candle.close, 16.9565);

      expect(candle.tickVolume, 143);
      expect(candle.spread, 499);
      expect(candle.realVolume, 0);
    });

    test('accepts integer JSON values for OHLC fields', () {
      final candle = Mt5Candle.fromJson({
        'bar_time': '2026-08-20T19:12:00Z',
        'open': 10,
        'high': 12,
        'low': 9,
        'close': 11,
        'tick_volume': 20,
        'spread': 5,
        'real_volume': 0,
      });

      expect(candle.open, 10.0);
      expect(candle.high, 12.0);
      expect(candle.low, 9.0);
      expect(candle.close, 11.0);
    });

    test('rejects invalid bar time', () {
      expect(
        () => Mt5Candle.fromJson({
          'bar_time': 'not-a-date',
          'open': 16.9562,
          'high': 16.9571,
          'low': 16.9558,
          'close': 16.9565,
          'tick_volume': 143,
          'spread': 499,
          'real_volume': 0,
        }),
        throwsA(isA<FormatException>()),
      );
    });

    test('rejects incomplete candle schema', () {
      expect(
        () => Mt5Candle.fromJson({
          'bar_time': '2026-08-20T19:12:00Z',
          'open': 16.9562,
          'high': 16.9571,
        }),
        throwsA(isA<FormatException>()),
      );
    });
  });
}
