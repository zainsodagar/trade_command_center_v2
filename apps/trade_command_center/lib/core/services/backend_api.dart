import '../config/api_config.dart';
import '../config/api_endpoints.dart';
import '../models/backend_system_status.dart';
import '../network/api_client.dart';
import '../network/api_exception.dart';

class BackendApi {
  BackendApi({ApiClient? client})
    : _client = client ?? ApiClient(),
      _ownsClient = client == null;

  final ApiClient _client;
  final bool _ownsClient;

  Future<BackendSystemStatus> getSystemStatus() async {
    final uri = ApiConfig.backendUri(ApiEndpoints.systemStatus);

    final result = await _client.getJson(uri);

    if (result is! Map<String, dynamic>) {
      throw ApiException(
        'Backend system status response must be a JSON object',
        uri: uri,
      );
    }

    try {
      return BackendSystemStatus.fromJson(result);
    } on FormatException catch (error) {
      throw ApiException(
        'Backend system status response has an invalid schema',
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
