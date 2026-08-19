import 'package:trade_command_center/core/models/mt5_instrument.dart';
import 'package:trade_command_center/features/markets/domain/instrument_catalog.dart';
import 'package:trade_command_center/features/markets/domain/instrument_catalog_loader.dart';

typedef InstrumentCatalogLoadCallback = Future<InstrumentCatalog> Function();

class FakeInstrumentCatalogLoader implements InstrumentCatalogLoader {
  FakeInstrumentCatalogLoader({required this.onLoad});

  final InstrumentCatalogLoadCallback onLoad;

  int loadCount = 0;
  bool closed = false;

  @override
  Future<InstrumentCatalog> load() {
    loadCount += 1;
    return onLoad();
  }

  @override
  void close() {
    closed = true;
  }
}

FakeInstrumentCatalogLoader buildSafeInstrumentCatalogLoader() {
  return FakeInstrumentCatalogLoader(
    onLoad: () async => buildInstrumentCatalog(),
  );
}

InstrumentCatalog buildInstrumentCatalog() {
  return InstrumentCatalog([
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
  ]);
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
