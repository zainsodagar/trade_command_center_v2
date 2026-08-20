import '../../../core/models/mt5_candle_series.dart';
import '../../../core/models/mt5_quote.dart';

abstract interface class MarketDataLoader {
  Future<Mt5Quote> loadQuote(String brokerSymbol);

  Future<Mt5CandleSeries> loadCandles({
    required String brokerSymbol,
    required String timeframe,
    required int count,
  });

  void close();
}
