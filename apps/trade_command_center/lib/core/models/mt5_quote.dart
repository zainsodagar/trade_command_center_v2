import 'json_reader.dart';

class Mt5Quote {
  const Mt5Quote({
    required this.brokerSymbol,
    required this.brokerPath,
    required this.brokerGroup,
    required this.digits,
    required this.point,
    required this.tradeMode,
    required this.newOrderAllowed,
    required this.referenceOnly,
    required this.visible,
    required this.selected,
    required this.quoteAvailable,
    required this.tickTime,
    required this.tickTimeMsc,
    required this.bid,
    required this.ask,
    required this.last,
    required this.volume,
    required this.volumeReal,
    required this.flags,
    required this.spread,
    required this.spreadPoints,
    required this.unavailableReason,
    required this.errorCode,
    required this.errorMessage,
  });

  final String brokerSymbol;
  final String brokerPath;
  final String brokerGroup;

  final int digits;
  final double point;

  final String tradeMode;

  final bool newOrderAllowed;
  final bool referenceOnly;
  final bool visible;
  final bool selected;
  final bool quoteAvailable;

  final DateTime? tickTime;
  final int? tickTimeMsc;

  final double? bid;
  final double? ask;
  final double? last;

  final int? volume;
  final double? volumeReal;
  final int? flags;

  final double? spread;
  final double? spreadPoints;

  final String? unavailableReason;
  final int? errorCode;
  final String? errorMessage;

  factory Mt5Quote.fromJson(Map<String, dynamic> json) {
    return Mt5Quote(
      brokerSymbol: readRequiredJsonField<String>(json, 'broker_symbol'),
      brokerPath: readRequiredJsonField<String>(json, 'broker_path'),
      brokerGroup: readRequiredJsonField<String>(json, 'broker_group'),
      digits: readRequiredJsonField<int>(json, 'digits'),
      point: readRequiredJsonField<num>(json, 'point').toDouble(),
      tradeMode: readRequiredJsonField<String>(json, 'trade_mode'),
      newOrderAllowed: readRequiredJsonField<bool>(json, 'new_order_allowed'),
      referenceOnly: readRequiredJsonField<bool>(json, 'reference_only'),
      visible: readRequiredJsonField<bool>(json, 'visible'),
      selected: readRequiredJsonField<bool>(json, 'selected'),
      quoteAvailable: readRequiredJsonField<bool>(json, 'quote_available'),
      tickTime: readNullableDateTimeField(json, 'tick_time'),
      tickTimeMsc: readNullableJsonField<int>(json, 'tick_time_msc'),
      bid: readNullableJsonField<num>(json, 'bid')?.toDouble(),
      ask: readNullableJsonField<num>(json, 'ask')?.toDouble(),
      last: readNullableJsonField<num>(json, 'last')?.toDouble(),
      volume: readNullableJsonField<int>(json, 'volume'),
      volumeReal: readNullableJsonField<num>(json, 'volume_real')?.toDouble(),
      flags: readNullableJsonField<int>(json, 'flags'),
      spread: readNullableJsonField<num>(json, 'spread')?.toDouble(),
      spreadPoints: readNullableJsonField<num>(
        json,
        'spread_points',
      )?.toDouble(),
      unavailableReason: readNullableJsonField<String>(
        json,
        'unavailable_reason',
      ),
      errorCode: readNullableJsonField<int>(json, 'error_code'),
      errorMessage: readNullableJsonField<String>(json, 'error_message'),
    );
  }
}
