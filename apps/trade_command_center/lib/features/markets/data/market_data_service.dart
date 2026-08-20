import '../../../core/models/mt5_candle_series.dart';
import '../../../core/models/mt5_quote.dart';
import '../../../core/services/agent_api.dart';
import '../domain/market_data_loader.dart';

class MarketDataService implements MarketDataLoader {
  MarketDataService({AgentApi? agentApi})
    : _agentApi = agentApi ?? AgentApi(),
      _ownsAgentApi = agentApi == null;

  final AgentApi _agentApi;
  final bool _ownsAgentApi;

  @override
  Future<Mt5Quote> loadQuote(String brokerSymbol) {
    return _agentApi.getMt5Quote(brokerSymbol);
  }

  @override
  Future<Mt5CandleSeries> loadCandles({
    required String brokerSymbol,
    required String timeframe,
    required int count,
  }) {
    return _agentApi.getMt5Candles(
      brokerSymbol: brokerSymbol,
      timeframe: timeframe,
      count: count,
    );
  }

  @override
  void close() {
    if (_ownsAgentApi) {
      _agentApi.close();
    }
  }
}
