import 'json_reader.dart';

class Mt5Status {
  const Mt5Status({
    required this.enabled,
    required this.terminalAvailable,
    required this.initialized,
    required this.connected,
    required this.accountLoggedIn,
    required this.executionEnabled,
    required this.liveTradingEnabled,
    required this.packageVersion,
    required this.terminalVersion,
    required this.terminalBuild,
    required this.terminalBuildDate,
    required this.tradeAllowed,
    required this.tradeApiDisabled,
    required this.dllsAllowed,
    required this.company,
    required this.terminalName,
    required this.terminalPath,
    required this.dataPath,
    required this.accountLoginMasked,
    required this.accountMode,
    required this.accountServer,
    required this.accountCompany,
    required this.accountCurrency,
    required this.accountLeverage,
    required this.accountTradeAllowed,
    required this.accountTradeExpert,
    required this.message,
    required this.checkedAt,
  });

  final bool enabled;

  final bool terminalAvailable;
  final bool initialized;
  final bool connected;
  final bool accountLoggedIn;

  final bool executionEnabled;
  final bool liveTradingEnabled;

  final String? packageVersion;

  final int? terminalVersion;
  final int? terminalBuild;
  final String? terminalBuildDate;

  final bool? tradeAllowed;
  final bool? tradeApiDisabled;
  final bool? dllsAllowed;

  final String? company;
  final String? terminalName;

  final String? terminalPath;
  final String? dataPath;

  final String? accountLoginMasked;
  final String? accountMode;
  final String? accountServer;
  final String? accountCompany;
  final String? accountCurrency;
  final int? accountLeverage;

  final bool? accountTradeAllowed;
  final bool? accountTradeExpert;

  final String message;
  final DateTime checkedAt;

  bool get isReadOnlySafe => !executionEnabled && !liveTradingEnabled;

  bool get isDemoAccount => accountMode?.toLowerCase() == 'demo';

  bool get isOperationalReadOnly =>
      enabled &&
      terminalAvailable &&
      connected &&
      accountLoggedIn &&
      isDemoAccount &&
      isReadOnlySafe;

  factory Mt5Status.fromJson(Map<String, dynamic> json) {
    return Mt5Status(
      enabled: readRequiredJsonField<bool>(json, 'enabled'),
      terminalAvailable: readRequiredJsonField<bool>(
        json,
        'terminal_available',
      ),
      initialized: readRequiredJsonField<bool>(json, 'initialized'),
      connected: readRequiredJsonField<bool>(json, 'connected'),
      accountLoggedIn: readRequiredJsonField<bool>(json, 'account_logged_in'),
      executionEnabled: readRequiredJsonField<bool>(json, 'execution_enabled'),
      liveTradingEnabled: readRequiredJsonField<bool>(
        json,
        'live_trading_enabled',
      ),
      packageVersion: readNullableJsonField<String>(json, 'package_version'),
      terminalVersion: readNullableJsonField<int>(json, 'terminal_version'),
      terminalBuild: readNullableJsonField<int>(json, 'terminal_build'),
      terminalBuildDate: readNullableJsonField<String>(
        json,
        'terminal_build_date',
      ),
      tradeAllowed: readNullableJsonField<bool>(json, 'trade_allowed'),
      tradeApiDisabled: readNullableJsonField<bool>(json, 'trade_api_disabled'),
      dllsAllowed: readNullableJsonField<bool>(json, 'dlls_allowed'),
      company: readNullableJsonField<String>(json, 'company'),
      terminalName: readNullableJsonField<String>(json, 'terminal_name'),
      terminalPath: readNullableJsonField<String>(json, 'terminal_path'),
      dataPath: readNullableJsonField<String>(json, 'data_path'),
      accountLoginMasked: readNullableJsonField<String>(
        json,
        'account_login_masked',
      ),
      accountMode: readNullableJsonField<String>(json, 'account_mode'),
      accountServer: readNullableJsonField<String>(json, 'account_server'),
      accountCompany: readNullableJsonField<String>(json, 'account_company'),
      accountCurrency: readNullableJsonField<String>(json, 'account_currency'),
      accountLeverage: readNullableJsonField<int>(json, 'account_leverage'),
      accountTradeAllowed: readNullableJsonField<bool>(
        json,
        'account_trade_allowed',
      ),
      accountTradeExpert: readNullableJsonField<bool>(
        json,
        'account_trade_expert',
      ),
      message: readRequiredJsonField<String>(json, 'message'),
      checkedAt: readRequiredDateTimeField(json, 'checked_at'),
    );
  }
}
