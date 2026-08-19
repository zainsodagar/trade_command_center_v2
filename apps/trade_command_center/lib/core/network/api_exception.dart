class ApiException implements Exception {
  const ApiException(this.message, {this.uri, this.statusCode, this.cause});

  final String message;
  final Uri? uri;
  final int? statusCode;
  final Object? cause;

  @override
  String toString() {
    final parts = <String>['ApiException: $message'];

    if (statusCode != null) {
      parts.add('status=$statusCode');
    }

    if (uri != null) {
      parts.add('uri=$uri');
    }

    return parts.join(', ');
  }
}
