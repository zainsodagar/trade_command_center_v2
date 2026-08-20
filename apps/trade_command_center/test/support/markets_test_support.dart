import 'package:trade_command_center/core/models/mt5_candle.dart';
import 'package:trade_command_center/core/models/mt5_candle_series.dart';
import 'package:trade_command_center/core/models/mt5_instrument.dart';
import 'package:trade_command_center/core/models/mt5_quote.dart';
import 'package:trade_command_center/features/markets/domain/instrument_catalog.dart';
import 'package:trade_command_center/features/markets/domain/instrument_catalog_loader.dart';
import 'package:trade_command_center/features/markets/domain/market_data_loader.dart';

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

typedef MarketQuoteLoadCallback =
    Future<Mt5Quote> Function(String brokerSymbol);

typedef MarketCandlesLoadCallback =
    Future<Mt5CandleSeries> Function({
      required String brokerSymbol,
      required String timeframe,
      required int count,
    });

class FakeMarketDataLoader implements MarketDataLoader {
  FakeMarketDataLoader({
    required this.onLoadQuote,
    required this.onLoadCandles,
  });

  final MarketQuoteLoadCallback onLoadQuote;
  final MarketCandlesLoadCallback onLoadCandles;

  int quoteLoadCount = 0;
  int candleLoadCount = 0;

  String? lastQuoteSymbol;
  String? lastCandleSymbol;
  String? lastTimeframe;
  int? lastCount;

  bool closed = false;

  @override
  Future<Mt5Quote> loadQuote(String brokerSymbol) {
    quoteLoadCount += 1;
    lastQuoteSymbol = brokerSymbol;

    return onLoadQuote(brokerSymbol);
  }

  @override
  Future<Mt5CandleSeries> loadCandles({
    required String brokerSymbol,
    required String timeframe,
    required int count,
  }) {
    candleLoadCount += 1;

    lastCandleSymbol = brokerSymbol;
    lastTimeframe = timeframe;
    lastCount = count;

    return onLoadCandles(
      brokerSymbol: brokerSymbol,
      timeframe: timeframe,
      count: count,
    );
  }

  @override
  void close() {
    closed = true;
  }
}

FakeMarketDataLoader buildSafeMarketDataLoader() {
  return FakeMarketDataLoader(
    onLoadQuote: (brokerSymbol) async {
      return buildMarketQuote(brokerSymbol: brokerSymbol);
    },
    onLoadCandles:
        ({required brokerSymbol, required timeframe, required count}) async {
          return buildMarketCandleSeries(
            brokerSymbol: brokerSymbol,
            timeframe: timeframe,
            countRequested: count,
          );
        },
  );
}

Mt5Quote buildMarketQuote({
  required String brokerSymbol,
  bool available = true,
  String? unavailableReason,
}) {
  return Mt5Quote(
    brokerSymbol: brokerSymbol,
    brokerPath: 'Test\\$brokerSymbol',
    brokerGroup: 'Test',
    digits: 5,
    point: 0.00001,
    tradeMode: 'full',
    newOrderAllowed: true,
    referenceOnly: false,
    visible: true,
    selected: true,
    quoteAvailable: available,
    tickTime: available ? DateTime.parse('2026-08-20T20:00:15Z') : null,
    tickTimeMsc: available ? 1787256015000 : null,
    bid: available ? 1.10000 : null,
    ask: available ? 1.10020 : null,
    last: available ? 1.10010 : null,
    volume: available ? 10 : null,
    volumeReal: available ? 10.0 : null,
    flags: available ? 1030 : null,
    spread: available ? 0.00020 : null,
    spreadPoints: available ? 20.0 : null,
    unavailableReason: available
        ? null
        : unavailableReason ?? 'quote_unavailable',
    errorCode: null,
    errorMessage: null,
  );
}

Mt5CandleSeries buildMarketCandleSeries({
  required String brokerSymbol,
  required String timeframe,
  required int countRequested,
  bool available = true,
  String? unavailableReason,
}) {
  final candles = available
      ? [
          Mt5Candle(
            barTime: DateTime.parse('2026-08-20T19:59:00Z'),
            open: 1.09980,
            high: 1.10010,
            low: 1.09970,
            close: 1.10000,
            tickVolume: 120,
            spread: 20,
            realVolume: 0,
          ),
          Mt5Candle(
            barTime: DateTime.parse('2026-08-20T20:00:00Z'),
            open: 1.10000,
            high: 1.10030,
            low: 1.09990,
            close: 1.10020,
            tickVolume: 143,
            spread: 20,
            realVolume: 0,
          ),
        ]
      : <Mt5Candle>[];

  return Mt5CandleSeries(
    brokerSymbol: brokerSymbol,
    brokerPath: 'Test\\$brokerSymbol',
    brokerGroup: 'Test',
    digits: 5,
    point: 0.00001,
    tradeMode: 'full',
    newOrderAllowed: true,
    referenceOnly: false,
    visibleBefore: true,
    selectedBefore: true,
    visibleAfter: true,
    selectedAfter: true,
    timeframe: timeframe,
    countRequested: countRequested,
    candlesAvailable: available,
    candleCount: candles.length,
    oldestCandleTime: available ? candles.first.barTime : null,
    latestCandleTime: available ? candles.last.barTime : null,
    candles: List<Mt5Candle>.unmodifiable(candles),
    unavailableReason: available
        ? null
        : unavailableReason ?? 'history_unavailable',
    errorCode: null,
    errorMessage: null,
  );
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
