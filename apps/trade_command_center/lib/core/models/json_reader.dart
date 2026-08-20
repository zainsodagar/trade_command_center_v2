T readRequiredJsonField<T>(Map<String, dynamic> json, String key) {
  if (!json.containsKey(key)) {
    throw FormatException('Required JSON field "$key" is missing.');
  }

  final value = json[key];

  if (value is! T) {
    throw FormatException('JSON field "$key" must be $T.');
  }

  return value;
}

T? readNullableJsonField<T>(Map<String, dynamic> json, String key) {
  if (!json.containsKey(key)) {
    return null;
  }

  final value = json[key];

  if (value == null) {
    return null;
  }

  if (value is! T) {
    throw FormatException('JSON field "$key" must be $T or null.');
  }

  return value;
}

DateTime readRequiredDateTimeField(Map<String, dynamic> json, String key) {
  final value = readRequiredJsonField<String>(json, key);

  final parsed = DateTime.tryParse(value);

  if (parsed == null) {
    throw FormatException('JSON field "$key" must contain a valid date-time.');
  }

  return parsed;
}

DateTime? readNullableDateTimeField(Map<String, dynamic> json, String key) {
  final value = readNullableJsonField<String>(json, key);

  if (value == null) {
    return null;
  }

  final parsed = DateTime.tryParse(value);

  if (parsed == null) {
    throw FormatException(
      'JSON field "$key" must contain a valid date-time or null.',
    );
  }

  return parsed;
}
