import '../config/api_config.dart';
import '../config/api_endpoints.dart';
import '../models/agent_status.dart';
import '../models/mt5_candle_series.dart';
import '../models/mt5_instrument.dart';
import '../models/mt5_quote.dart';
import '../models/mt5_status.dart';
import '../network/api_client.dart';
import '../network/api_exception.dart';

class AgentApi {
  AgentApi({ApiClient? client})
    : _client = client ?? ApiClient(),
      _ownsClient = client == null;

  final ApiClient _client;
  final bool _ownsClient;

  Future<AgentStatus> getAgentStatus() async {
    final uri = ApiConfig.agentUri(ApiEndpoints.agentStatus);

    final result = await _client.getJson(uri);

    if (result is! Map<String, dynamic>) {
      throw ApiException(
        'Agent status response must be a JSON object',
        uri: uri,
      );
    }

    try {
      return AgentStatus.fromJson(result);
    } on FormatException catch (error) {
      throw ApiException(
        'Agent status response has an invalid schema',
        uri: uri,
        cause: error,
      );
    }
  }

  Future<Mt5Status> getMt5Status() async {
    final uri = ApiConfig.agentUri(ApiEndpoints.mt5Status);

    final result = await _client.getJson(uri);

    if (result is! Map<String, dynamic>) {
      throw ApiException('MT5 status response must be a JSON object', uri: uri);
    }

    try {
      return Mt5Status.fromJson(result);
    } on FormatException catch (error) {
      throw ApiException(
        'MT5 status response has an invalid schema',
        uri: uri,
        cause: error,
      );
    }
  }

  Future<List<Mt5Instrument>> getMt5Instruments() async {
    final uri = ApiConfig.agentUri(ApiEndpoints.mt5Instruments);

    final result = await _client.getJson(uri);

    if (result is! List<dynamic>) {
      throw ApiException(
        'MT5 instruments response must be a JSON array',
        uri: uri,
      );
    }

    try {
      final instruments = result
          .map((item) {
            if (item is! Map<String, dynamic>) {
              throw const FormatException(
                'MT5 instrument entry must be a JSON object.',
              );
            }

            return Mt5Instrument.fromJson(item);
          })
          .toList(growable: false);

      return List<Mt5Instrument>.unmodifiable(instruments);
    } on FormatException catch (error) {
      throw ApiException(
        'MT5 instruments response has an invalid schema',
        uri: uri,
        cause: error,
      );
    }
  }

  Future<Mt5Quote> getMt5Quote(String brokerSymbol) async {
    final uri = ApiConfig.agentUri(
      ApiEndpoints.mt5Quote,
      queryParameters: {'broker_symbol': brokerSymbol},
    );

    final result = await _client.getJson(uri);

    if (result is! Map<String, dynamic>) {
      throw ApiException('MT5 quote response must be a JSON object', uri: uri);
    }

    try {
      return Mt5Quote.fromJson(result);
    } on FormatException catch (error) {
      throw ApiException(
        'MT5 quote response has an invalid schema',
        uri: uri,
        cause: error,
      );
    }
  }

  Future<Mt5CandleSeries> getMt5Candles({
    required String brokerSymbol,
    String timeframe = 'M1',
    int count = 100,
  }) async {
    final uri = ApiConfig.agentUri(
      ApiEndpoints.mt5Candles,
      queryParameters: {
        'broker_symbol': brokerSymbol,
        'timeframe': timeframe,
        'count': count.toString(),
      },
    );

    final result = await _client.getJson(uri);

    if (result is! Map<String, dynamic>) {
      throw ApiException(
        'MT5 candles response must be a JSON object',
        uri: uri,
      );
    }

    try {
      return Mt5CandleSeries.fromJson(result);
    } on FormatException catch (error) {
      throw ApiException(
        'MT5 candles response has an invalid schema',
        uri: uri,
        cause: error,
      );
    }
  }

  void close() {
    if (_ownsClient) {
      _client.close();
    }
  }
}
