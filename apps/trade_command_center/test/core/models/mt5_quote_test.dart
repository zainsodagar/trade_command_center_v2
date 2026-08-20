import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/mt5_quote.dart';

void main() {
  group('Mt5Quote', () {
    test('parses available live PXBT quote', () {
      final quote = Mt5Quote.fromJson({
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
        'spread': 48.89999999999418,
        'spread_points': 488.9999999999,
        'unavailable_reason': null,
        'error_code': null,
        'error_message': null,
      });

      expect(quote.brokerSymbol, 'BTCUSDT');
      expect(quote.brokerPath, r'Crypto\BTCUSDT');
      expect(quote.brokerGroup, 'Crypto');

      expect(quote.digits, 1);
      expect(quote.point, 0.1);
      expect(quote.tradeMode, 'full');

      expect(quote.newOrderAllowed, isTrue);
      expect(quote.referenceOnly, isFalse);
      expect(quote.visible, isTrue);
      expect(quote.selected, isTrue);
      expect(quote.quoteAvailable, isTrue);

      expect(quote.tickTime, DateTime.parse('2026-08-20T17:27:34Z'));
      expect(quote.tickTimeMsc, 1787246854847);

      expect(quote.bid, 72740.5);
      expect(quote.ask, 72789.4);
      expect(quote.last, 0.0);

      expect(quote.volume, 0);
      expect(quote.volumeReal, 0.0);
      expect(quote.flags, 1030);

      expect(quote.spread, 48.89999999999418);
      expect(quote.spreadPoints, 488.9999999999);

      expect(quote.unavailableReason, isNull);
      expect(quote.errorCode, isNull);
      expect(quote.errorMessage, isNull);
    });

    test('parses unavailable quote with nullable market data', () {
      final quote = Mt5Quote.fromJson({
        'broker_symbol': 'EURUSD',
        'broker_path': r'Forex\EURUSD',
        'broker_group': 'Forex',
        'digits': 5,
        'point': 0.00001,
        'trade_mode': 'full',
        'new_order_allowed': true,
        'reference_only': false,
        'visible': false,
        'selected': false,
        'quote_available': false,
        'tick_time': null,
        'tick_time_msc': null,
        'bid': null,
        'ask': null,
        'last': null,
        'volume': null,
        'volume_real': null,
        'flags': null,
        'spread': null,
        'spread_points': null,
        'unavailable_reason': 'symbol_not_selected',
        'error_code': null,
        'error_message': null,
      });

      expect(quote.brokerSymbol, 'EURUSD');

      expect(quote.quoteAvailable, isFalse);
      expect(quote.selected, isFalse);

      expect(quote.tickTime, isNull);
      expect(quote.tickTimeMsc, isNull);

      expect(quote.bid, isNull);
      expect(quote.ask, isNull);
      expect(quote.last, isNull);

      expect(quote.volume, isNull);
      expect(quote.volumeReal, isNull);
      expect(quote.flags, isNull);

      expect(quote.spread, isNull);
      expect(quote.spreadPoints, isNull);

      expect(quote.unavailableReason, 'symbol_not_selected');
      expect(quote.errorCode, isNull);
      expect(quote.errorMessage, isNull);
    });

    test('rejects invalid nullable tick time', () {
      expect(
        () => Mt5Quote.fromJson({
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
          'tick_time': 'not-a-date',
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
        }),
        throwsA(isA<FormatException>()),
      );
    });
  });
}
