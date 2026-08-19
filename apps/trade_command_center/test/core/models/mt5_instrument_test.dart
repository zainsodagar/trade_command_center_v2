import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/mt5_instrument.dart';

void main() {
  group('Mt5Instrument', () {
    test('parses normal full-trade PXBT instrument', () {
      final instrument = Mt5Instrument.fromJson({
        'broker_symbol': 'AAPL',
        'broker_path': r'Shares\AAPL',
        'broker_group': 'Shares',
        'description': 'Apple Inc',
        'currency_base': 'USD',
        'currency_profit': 'USD',
        'currency_margin': 'USD',
        'digits': 2,
        'point': 0.01,
        'contract_size': 100.0,
        'volume_min': 0.01,
        'volume_max': 50.0,
        'volume_step': 0.01,
        'trade_mode': 'full',
        'trade_calc_mode': 4,
        'order_mode': 127,
        'new_order_allowed': true,
        'reference_only': false,
        'visible': false,
        'selected': false,
      });

      expect(instrument.brokerSymbol, 'AAPL');

      expect(instrument.brokerPath, r'Shares\AAPL');

      expect(instrument.brokerGroup, 'Shares');

      expect(instrument.description, 'Apple Inc');

      expect(instrument.currencyBase, 'USD');

      expect(instrument.digits, 2);

      expect(instrument.point, 0.01);

      expect(instrument.contractSize, 100.0);

      expect(instrument.volumeMin, 0.01);

      expect(instrument.volumeMax, 50.0);

      expect(instrument.volumeStep, 0.01);

      expect(instrument.isFullTradeMode, isTrue);

      expect(instrument.isCloseOnly, isFalse);

      expect(instrument.isDisabled, isFalse);

      expect(instrument.newOrderAllowed, isTrue);

      expect(instrument.referenceOnly, isFalse);

      expect(instrument.canOpenNewOrders, isTrue);

      expect(instrument.availabilityLabel, 'Available');
    });

    test('parses disabled PXBT reference-only symbol safely', () {
      final instrument = Mt5Instrument.fromJson({
        'broker_symbol': 'BTCUSD',
        'broker_path': r'RefSymbols\BTCUSD',
        'broker_group': 'RefSymbols',
        'description': 'Conversion only',
        'currency_base': 'BTC',
        'currency_profit': 'USD',
        'currency_margin': 'USD',
        'digits': 1,
        'point': 0.1,
        'contract_size': 1.0,
        'volume_min': 0.0001,
        'volume_max': 100000000000.0,
        'volume_step': 0.0001,
        'trade_mode': 'disabled',
        'trade_calc_mode': 0,
        'order_mode': 127,
        'new_order_allowed': false,
        'reference_only': true,
        'visible': true,
        'selected': true,
      });

      expect(instrument.brokerSymbol, 'BTCUSD');

      expect(instrument.brokerGroup, 'RefSymbols');

      expect(instrument.referenceOnly, isTrue);

      expect(instrument.isDisabled, isTrue);

      expect(instrument.isFullTradeMode, isFalse);

      expect(instrument.newOrderAllowed, isFalse);

      expect(instrument.canOpenNewOrders, isFalse);

      expect(instrument.availabilityLabel, 'Reference only');
    });

    test('parses PXBT close-only symbol without treating it as available', () {
      final instrument = Mt5Instrument.fromJson({
        'broker_symbol': 'TONUSDT',
        'broker_path': r'Crypto\TONUSDT',
        'broker_group': 'Crypto',
        'description': 'Toncoin vs USDT',
        'currency_base': 'UST',
        'currency_profit': 'UST',
        'currency_margin': 'UST',
        'digits': 4,
        'point': 0.0001,
        'contract_size': 100.0,
        'volume_min': 0.1,
        'volume_max': 1000.0,
        'volume_step': 0.1,
        'trade_mode': 'close_only',
        'trade_calc_mode': 4,
        'order_mode': 127,
        'new_order_allowed': false,
        'reference_only': false,
        'visible': false,
        'selected': false,
      });

      expect(instrument.brokerSymbol, 'TONUSDT');

      expect(instrument.brokerGroup, 'Crypto');

      expect(instrument.isCloseOnly, isTrue);

      expect(instrument.isDisabled, isFalse);

      expect(instrument.newOrderAllowed, isFalse);

      expect(instrument.referenceOnly, isFalse);

      expect(instrument.canOpenNewOrders, isFalse);

      expect(instrument.availabilityLabel, 'Close only');
    });

    test('rejects incomplete instrument schema', () {
      expect(
        () => Mt5Instrument.fromJson({
          'broker_path': r'Shares\AAPL',
          'broker_group': 'Shares',
        }),
        throwsA(isA<FormatException>()),
      );
    });
  });
}
