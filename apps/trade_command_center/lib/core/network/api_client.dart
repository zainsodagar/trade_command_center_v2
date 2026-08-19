import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import 'api_exception.dart';

class ApiClient {
  ApiClient({http.Client? client, this.timeout = const Duration(seconds: 5)})
    : _client = client ?? http.Client(),
      _ownsClient = client == null;

  final http.Client _client;
  final bool _ownsClient;

  final Duration timeout;

  Future<Object?> getJson(Uri uri) async {
    late final http.Response response;

    try {
      response = await _client
          .get(uri, headers: const {'Accept': 'application/json'})
          .timeout(timeout);
    } on TimeoutException catch (error) {
      throw ApiException('Request timed out', uri: uri, cause: error);
    } on http.ClientException catch (error) {
      throw ApiException('Unable to connect to API', uri: uri, cause: error);
    } catch (error) {
      throw ApiException('API request failed', uri: uri, cause: error);
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(
        _extractErrorMessage(response),
        uri: uri,
        statusCode: response.statusCode,
      );
    }

    final body = response.body.trim();

    if (body.isEmpty) {
      return null;
    }

    try {
      return jsonDecode(body);
    } on FormatException catch (error) {
      throw ApiException(
        'API response was not valid JSON',
        uri: uri,
        statusCode: response.statusCode,
        cause: error,
      );
    }
  }

  String _extractErrorMessage(http.Response response) {
    final body = response.body.trim();

    if (body.isEmpty) {
      return 'API returned HTTP ${response.statusCode}';
    }

    try {
      final decoded = jsonDecode(body);

      if (decoded is Map<String, dynamic>) {
        final detail = decoded['detail'];

        if (detail is String && detail.trim().isNotEmpty) {
          return detail;
        }
      }
    } on FormatException {
      // Fall back to a generic HTTP error below.
    }

    return 'API returned HTTP ${response.statusCode}';
  }

  void close() {
    if (_ownsClient) {
      _client.close();
    }
  }
}
