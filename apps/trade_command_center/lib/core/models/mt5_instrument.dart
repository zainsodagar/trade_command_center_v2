import 'json_reader.dart';

class Mt5Instrument {
  const Mt5Instrument({
    required this.brokerSymbol,
    required this.brokerPath,
    required this.brokerGroup,
    required this.description,
    required this.currencyBase,
    required this.currencyProfit,
    required this.currencyMargin,
    required this.digits,
    required this.point,
    required this.contractSize,
    required this.volumeMin,
    required this.volumeMax,
    required this.volumeStep,
    required this.tradeMode,
    required this.tradeCalcMode,
    required this.orderMode,
    required this.newOrderAllowed,
    required this.referenceOnly,
    required this.visible,
    required this.selected,
  });

  final String brokerSymbol;
  final String brokerPath;
  final String brokerGroup;
  final String description;

  final String currencyBase;
  final String currencyProfit;
  final String currencyMargin;

  final int digits;
  final double point;
  final double contractSize;

  final double volumeMin;
  final double volumeMax;
  final double volumeStep;

  final String tradeMode;
  final int tradeCalcMode;
  final int orderMode;

  final bool newOrderAllowed;
  final bool referenceOnly;
  final bool visible;
  final bool selected;

  bool get isFullTradeMode => tradeMode.toLowerCase() == 'full';

  bool get isCloseOnly => tradeMode.toLowerCase() == 'close_only';

  bool get isDisabled => tradeMode.toLowerCase() == 'disabled';

  bool get canOpenNewOrders =>
      newOrderAllowed && !referenceOnly && isFullTradeMode;

  String get availabilityLabel {
    if (referenceOnly) {
      return 'Reference only';
    }

    if (isCloseOnly) {
      return 'Close only';
    }

    if (isDisabled || !newOrderAllowed) {
      return 'New orders disabled';
    }

    return 'Available';
  }

  factory Mt5Instrument.fromJson(Map<String, dynamic> json) {
    return Mt5Instrument(
      brokerSymbol: readRequiredJsonField<String>(json, 'broker_symbol'),
      brokerPath: readRequiredJsonField<String>(json, 'broker_path'),
      brokerGroup: readRequiredJsonField<String>(json, 'broker_group'),
      description: readRequiredJsonField<String>(json, 'description'),
      currencyBase: readRequiredJsonField<String>(json, 'currency_base'),
      currencyProfit: readRequiredJsonField<String>(json, 'currency_profit'),
      currencyMargin: readRequiredJsonField<String>(json, 'currency_margin'),
      digits: readRequiredJsonField<int>(json, 'digits'),
      point: readRequiredJsonField<num>(json, 'point').toDouble(),
      contractSize: readRequiredJsonField<num>(
        json,
        'contract_size',
      ).toDouble(),
      volumeMin: readRequiredJsonField<num>(json, 'volume_min').toDouble(),
      volumeMax: readRequiredJsonField<num>(json, 'volume_max').toDouble(),
      volumeStep: readRequiredJsonField<num>(json, 'volume_step').toDouble(),
      tradeMode: readRequiredJsonField<String>(json, 'trade_mode'),
      tradeCalcMode: readRequiredJsonField<int>(json, 'trade_calc_mode'),
      orderMode: readRequiredJsonField<int>(json, 'order_mode'),
      newOrderAllowed: readRequiredJsonField<bool>(json, 'new_order_allowed'),
      referenceOnly: readRequiredJsonField<bool>(json, 'reference_only'),
      visible: readRequiredJsonField<bool>(json, 'visible'),
      selected: readRequiredJsonField<bool>(json, 'selected'),
    );
  }
}
