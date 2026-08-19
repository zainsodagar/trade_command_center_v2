class ApiConfig {
  ApiConfig._();

  static const String backendBaseUrl = String.fromEnvironment(
    'TCC_BACKEND_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );

  static const String agentBaseUrl = String.fromEnvironment(
    'TCC_AGENT_BASE_URL',
    defaultValue: 'http://127.0.0.1:8765',
  );

  static Uri backendUri(String path, {Map<String, String>? queryParameters}) {
    return _buildUri(backendBaseUrl, path, queryParameters);
  }

  static Uri agentUri(String path, {Map<String, String>? queryParameters}) {
    return _buildUri(agentBaseUrl, path, queryParameters);
  }

  static Uri _buildUri(
    String baseUrl,
    String path,
    Map<String, String>? queryParameters,
  ) {
    final normalizedPath = path.startsWith('/') ? path : '/$path';

    final uri = Uri.parse('$baseUrl$normalizedPath');

    if (queryParameters == null || queryParameters.isEmpty) {
      return uri;
    }

    return uri.replace(queryParameters: queryParameters);
  }
}
