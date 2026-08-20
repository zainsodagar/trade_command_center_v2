import 'json_reader.dart';
import 'mt5_candle.dart';

class Mt5CandleSeries {
  const Mt5CandleSeries({
    required this.brokerSymbol,
    required this.brokerPath,
    required this.brokerGroup,
    required this.digits,
    required this.point,
    required this.tradeMode,
    required this.newOrderAllowed,
    required this.referenceOnly,
    required this.visibleBefore,
    required this.selectedBefore,
    required this.visibleAfter,
    required this.selectedAfter,
    required this.timeframe,
    required this.countRequested,
    required this.candlesAvailable,
    required this.candleCount,
    required this.oldestCandleTime,
    required this.latestCandleTime,
    required this.candles,
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

  final bool visibleBefore;
  final bool selectedBefore;
  final bool visibleAfter;
  final bool selectedAfter;

  final String timeframe;
  final int countRequested;

  final bool candlesAvailable;
  final int candleCount;

  final DateTime? oldestCandleTime;
  final DateTime? latestCandleTime;

  final List<Mt5Candle> candles;

  final String? unavailableReason;
  final int? errorCode;
  final String? errorMessage;

  factory Mt5CandleSeries.fromJson(Map<String, dynamic> json) {
    final rawCandles = readRequiredJsonField<List<dynamic>>(json, 'candles');

    final candles = rawCandles
        .map((item) {
          if (item is! Map<String, dynamic>) {
            throw const FormatException(
              'MT5 candle entry must be a JSON object.',
            );
          }

          return Mt5Candle.fromJson(item);
        })
        .toList(growable: false);

    return Mt5CandleSeries(
      brokerSymbol: readRequiredJsonField<String>(json, 'broker_symbol'),
      brokerPath: readRequiredJsonField<String>(json, 'broker_path'),
      brokerGroup: readRequiredJsonField<String>(json, 'broker_group'),
      digits: readRequiredJsonField<int>(json, 'digits'),
      point: readRequiredJsonField<num>(json, 'point').toDouble(),
      tradeMode: readRequiredJsonField<String>(json, 'trade_mode'),
      newOrderAllowed: readRequiredJsonField<bool>(json, 'new_order_allowed'),
      referenceOnly: readRequiredJsonField<bool>(json, 'reference_only'),
      visibleBefore: readRequiredJsonField<bool>(json, 'visible_before'),
      selectedBefore: readRequiredJsonField<bool>(json, 'selected_before'),
      visibleAfter: readRequiredJsonField<bool>(json, 'visible_after'),
      selectedAfter: readRequiredJsonField<bool>(json, 'selected_after'),
      timeframe: readRequiredJsonField<String>(json, 'timeframe'),
      countRequested: readRequiredJsonField<int>(json, 'count_requested'),
      candlesAvailable: readRequiredJsonField<bool>(json, 'candles_available'),
      candleCount: readRequiredJsonField<int>(json, 'candle_count'),
      oldestCandleTime: readNullableDateTimeField(json, 'oldest_candle_time'),
      latestCandleTime: readNullableDateTimeField(json, 'latest_candle_time'),
      candles: List<Mt5Candle>.unmodifiable(candles),
      unavailableReason: readNullableJsonField<String>(
        json,
        'unavailable_reason',
      ),
      errorCode: readNullableJsonField<int>(json, 'error_code'),
      errorMessage: readNullableJsonField<String>(json, 'error_message'),
    );
  }
}
