import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/mt5_instrument.dart';
import 'package:trade_command_center/features/markets/domain/instrument_catalog.dart';

void main() {
  group('InstrumentCatalog', () {
    test('discovers broker groups dynamically and counts catalogue state', () {
      final catalog = InstrumentCatalog(_catalogue());

      expect(catalog.totalCount, 7);

      expect(catalog.brokerGroups, [
        'Commodities',
        'Crypto',
        'Forex',
        'Indices',
        'RefSymbols',
        'Shares',
      ]);

      expect(catalog.groupCounts, {
        'Forex': 1,
        'Shares': 1,
        'Crypto': 2,
        'RefSymbols': 1,
        'Commodities': 1,
        'Indices': 1,
      });

      expect(catalog.newOrdersAvailableCount, 5);

      expect(catalog.newOrdersBlockedCount, 2);

      expect(catalog.referenceOnlyCount, 1);

      expect(catalog.closeOnlyCount, 1);
    });

    test('searches symbol description path and group case-insensitively', () {
      final catalog = InstrumentCatalog(_catalogue());

      final bySymbol = catalog.filter(query: 'eurusd');

      expect(bySymbol.map((instrument) => instrument.brokerSymbol), ['EURUSD']);

      final byDescription = catalog.filter(query: 'apple');

      expect(byDescription.map((instrument) => instrument.brokerSymbol), [
        'AAPL',
      ]);

      final byPath = catalog.filter(query: 'major');

      expect(byPath.map((instrument) => instrument.brokerSymbol), ['EURUSD']);

      final byGroup = catalog.filter(query: 'indices');

      expect(byGroup.map((instrument) => instrument.brokerSymbol), ['AUS200']);
    });

    test('combines search text with dynamic broker-group filtering', () {
      final catalog = InstrumentCatalog(_catalogue());

      final cryptoBitcoin = catalog.filter(query: 'btc', brokerGroup: 'Crypto');

      expect(cryptoBitcoin.length, 1);

      expect(cryptoBitcoin.single.brokerSymbol, 'BTCUSDT');

      final referenceBitcoin = catalog.filter(
        query: 'btc',
        brokerGroup: 'RefSymbols',
      );

      expect(referenceBitcoin.length, 1);

      expect(referenceBitcoin.single.brokerSymbol, 'BTCUSD');
    });

    test('filters instruments that can open new orders', () {
      final catalog = InstrumentCatalog(_catalogue());

      final available = catalog.filter(
        availability: InstrumentAvailabilityFilter.newOrdersAvailable,
      );

      expect(available.length, 5);

      expect(
        available.every((instrument) => instrument.canOpenNewOrders),
        isTrue,
      );

      expect(
        available.any((instrument) => instrument.brokerSymbol == 'BTCUSD'),
        isFalse,
      );

      expect(
        available.any((instrument) => instrument.brokerSymbol == 'TONUSDT'),
        isFalse,
      );
    });

    test('filters all new-order-blocked instruments without losing reason', () {
      final catalog = InstrumentCatalog(_catalogue());

      final blocked = catalog.filter(
        availability: InstrumentAvailabilityFilter.newOrdersBlocked,
      );

      expect(blocked.map((instrument) => instrument.brokerSymbol), [
        'BTCUSD',
        'TONUSDT',
      ]);

      expect(blocked[0].availabilityLabel, 'Reference only');

      expect(blocked[1].availabilityLabel, 'Close only');
    });

    test('filters reference-only and close-only symbols independently', () {
      final catalog = InstrumentCatalog(_catalogue());

      final referenceOnly = catalog.filter(
        availability: InstrumentAvailabilityFilter.referenceOnly,
      );

      expect(referenceOnly.length, 1);

      expect(referenceOnly.single.brokerSymbol, 'BTCUSD');

      expect(referenceOnly.single.referenceOnly, isTrue);

      final closeOnly = catalog.filter(
        availability: InstrumentAvailabilityFilter.closeOnly,
      );

      expect(closeOnly.length, 1);

      expect(closeOnly.single.brokerSymbol, 'TONUSDT');

      expect(closeOnly.single.isCloseOnly, isTrue);
    });
  });
}

List<Mt5Instrument> _catalogue() {
  return [
    _instrument(
      symbol: 'EURUSD',
      path: r'Forex\Major\EURUSD',
      group: 'Forex',
      description: 'Euro vs US Dollar',
    ),
    _instrument(
      symbol: 'AAPL',
      path: r'Shares\AAPL',
      group: 'Shares',
      description: 'Apple Inc',
    ),
    _instrument(
      symbol: 'BTCUSDT',
      path: r'Crypto\BTCUSDT',
      group: 'Crypto',
      description: 'Bitcoin vs USDT',
    ),
    _instrument(
      symbol: 'BTCUSD',
      path: r'RefSymbols\BTCUSD',
      group: 'RefSymbols',
      description: 'Conversion only',
      tradeMode: 'disabled',
      newOrderAllowed: false,
      referenceOnly: true,
    ),
    _instrument(
      symbol: 'TONUSDT',
      path: r'Crypto\TONUSDT',
      group: 'Crypto',
      description: 'Toncoin vs USDT',
      tradeMode: 'close_only',
      newOrderAllowed: false,
    ),
    _instrument(
      symbol: 'BRENT',
      path: r'Commodities\BRENT',
      group: 'Commodities',
      description: 'Brent Crude Oil',
    ),
    _instrument(
      symbol: 'AUS200',
      path: r'Indices\AUS200',
      group: 'Indices',
      description: 'Australia top 200 index',
    ),
  ];
}

Mt5Instrument _instrument({
  required String symbol,
  required String path,
  required String group,
  required String description,
  String tradeMode = 'full',
  bool newOrderAllowed = true,
  bool referenceOnly = false,
}) {
  return Mt5Instrument(
    brokerSymbol: symbol,
    brokerPath: path,
    brokerGroup: group,
    description: description,
    currencyBase: 'USD',
    currencyProfit: 'USD',
    currencyMargin: 'USD',
    digits: 2,
    point: 0.01,
    contractSize: 100.0,
    volumeMin: 0.01,
    volumeMax: 100.0,
    volumeStep: 0.01,
    tradeMode: tradeMode,
    tradeCalcMode: 4,
    orderMode: 127,
    newOrderAllowed: newOrderAllowed,
    referenceOnly: referenceOnly,
    visible: false,
    selected: false,
  );
}
