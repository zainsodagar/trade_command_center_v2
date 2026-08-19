import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:trade_command_center/core/network/api_client.dart';
import 'package:trade_command_center/core/network/api_exception.dart';

void main() {
  group('ApiClient', () {
    test('decodes successful JSON object response', () async {
      final mockClient = MockClient((request) async {
        expect(request.method, 'GET');

        expect(request.headers['Accept'], 'application/json');

        return http.Response(
          '''
              {
                "status": "ok",
                "execution_enabled": false
              }
              ''',
          200,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockClient);

      final result = await apiClient.getJson(
        Uri.parse('http://127.0.0.1:8000/health'),
      );

      expect(result, isA<Map<String, dynamic>>());

      final json = result! as Map<String, dynamic>;

      expect(json['status'], 'ok');

      expect(json['execution_enabled'], isFalse);

      apiClient.close();
    });

    test('decodes successful JSON list response', () async {
      final mockClient = MockClient((request) async {
        return http.Response('''
              [
                {
                  "broker_symbol": "EURUSD"
                },
                {
                  "broker_symbol": "BTCUSD"
                }
              ]
              ''', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      final result = await apiClient.getJson(
        Uri.parse('http://127.0.0.1:8765/api/v1/mt5/instruments'),
      );

      expect(result, isA<List<dynamic>>());

      final json = result! as List<dynamic>;

      expect(json.length, 2);

      apiClient.close();
    });

    test('returns null for successful empty response', () async {
      final mockClient = MockClient((request) async {
        return http.Response('', 204);
      });

      final apiClient = ApiClient(client: mockClient);

      final result = await apiClient.getJson(
        Uri.parse('http://127.0.0.1:8000/health'),
      );

      expect(result, isNull);

      apiClient.close();
    });

    test('extracts FastAPI detail from non-success response', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          '''
              {
                "detail": "MT5 integration is disabled"
              }
              ''',
          503,
          headers: {'content-type': 'application/json'},
        );
      });

      final apiClient = ApiClient(client: mockClient);

      final uri = Uri.parse('http://127.0.0.1:8765/api/v1/mt5/account');

      await expectLater(
        apiClient.getJson(uri),
        throwsA(
          isA<ApiException>()
              .having(
                (error) => error.message,
                'message',
                'MT5 integration is disabled',
              )
              .having((error) => error.statusCode, 'statusCode', 503)
              .having((error) => error.uri, 'uri', uri),
        ),
      );

      apiClient.close();
    });

    test('rejects invalid JSON response', () async {
      final mockClient = MockClient((request) async {
        return http.Response('not-json', 200);
      });

      final apiClient = ApiClient(client: mockClient);

      await expectLater(
        apiClient.getJson(Uri.parse('http://127.0.0.1:8000/health')),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'API response was not valid JSON',
          ),
        ),
      );

      apiClient.close();
    });

    test('converts connection failure into ApiException', () async {
      final mockClient = MockClient((request) async {
        throw http.ClientException('Connection refused', request.url);
      });

      final apiClient = ApiClient(client: mockClient);

      await expectLater(
        apiClient.getJson(Uri.parse('http://127.0.0.1:8000/health')),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'Unable to connect to API',
          ),
        ),
      );

      apiClient.close();
    });

    test('converts request timeout into ApiException', () async {
      final mockClient = MockClient((request) async {
        await Future<void>.delayed(const Duration(milliseconds: 50));

        return http.Response('{"status":"ok"}', 200);
      });

      final apiClient = ApiClient(
        client: mockClient,
        timeout: const Duration(milliseconds: 1),
      );

      await expectLater(
        apiClient.getJson(Uri.parse('http://127.0.0.1:8000/health')),
        throwsA(
          isA<ApiException>().having(
            (error) => error.message,
            'message',
            'Request timed out',
          ),
        ),
      );

      apiClient.close();
    });
  });
}
