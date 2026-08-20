import 'json_reader.dart';

class Mt5Candle {
  const Mt5Candle({
    required this.barTime,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.tickVolume,
    required this.spread,
    required this.realVolume,
  });

  final DateTime barTime;

  final double open;
  final double high;
  final double low;
  final double close;

  final int tickVolume;
  final int spread;
  final int realVolume;

  factory Mt5Candle.fromJson(Map<String, dynamic> json) {
    return Mt5Candle(
      barTime: readRequiredDateTimeField(json, 'bar_time'),
      open: readRequiredJsonField<num>(json, 'open').toDouble(),
      high: readRequiredJsonField<num>(json, 'high').toDouble(),
      low: readRequiredJsonField<num>(json, 'low').toDouble(),
      close: readRequiredJsonField<num>(json, 'close').toDouble(),
      tickVolume: readRequiredJsonField<int>(json, 'tick_volume'),
      spread: readRequiredJsonField<int>(json, 'spread'),
      realVolume: readRequiredJsonField<int>(json, 'real_volume'),
    );
  }
}
