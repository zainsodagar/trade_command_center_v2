import 'dart:io';

import 'package:trade_command_center/core/models/mt5_instrument.dart';
import 'package:trade_command_center/core/services/agent_api.dart';

Future<void> main() async {
  final agentApi = AgentApi();

  try {
    final instruments = await agentApi.getMt5Instruments();

    final groupCounts = <String, int>{};

    for (final instrument in instruments) {
      groupCounts.update(
        instrument.brokerGroup,
        (count) => count + 1,
        ifAbsent: () => 1,
      );
    }

    final newOrderAllowed = instruments
        .where((instrument) => instrument.newOrderAllowed)
        .length;

    final newOrderBlocked = instruments
        .where((instrument) => !instrument.newOrderAllowed)
        .length;

    final referenceOnly = instruments
        .where((instrument) => instrument.referenceOnly)
        .length;

    final fullTradeMode = instruments
        .where((instrument) => instrument.isFullTradeMode)
        .length;

    final disabled = instruments
        .where((instrument) => instrument.isDisabled)
        .length;

    final closeOnly = instruments
        .where((instrument) => instrument.isCloseOnly)
        .length;

    stdout.writeln('PXBT MT5 Instrument Catalogue:');
    stdout.writeln('  total = ${instruments.length}');

    stdout.writeln();

    stdout.writeln('Groups:');

    for (final group in [
      'Forex',
      'Commodities',
      'Crypto',
      'Indices',
      'Shares',
      'RefSymbols',
    ]) {
      stdout.writeln('  $group = ${groupCounts[group] ?? 0}');
    }

    stdout.writeln();

    stdout.writeln('Trade modes:');
    stdout.writeln('  full = $fullTradeMode');
    stdout.writeln('  disabled = $disabled');
    stdout.writeln('  closeOnly = $closeOnly');

    stdout.writeln();

    stdout.writeln('Order metadata:');
    stdout.writeln('  newOrderAllowed = $newOrderAllowed');
    stdout.writeln('  newOrderBlocked = $newOrderBlocked');
    stdout.writeln('  referenceOnly = $referenceOnly');

    _assertCount(
      label: 'Total instruments',
      actual: instruments.length,
      expected: 207,
    );

    _assertCount(
      label: 'Forex instruments',
      actual: groupCounts['Forex'] ?? 0,
      expected: 99,
    );

    _assertCount(
      label: 'Commodities instruments',
      actual: groupCounts['Commodities'] ?? 0,
      expected: 36,
    );

    _assertCount(
      label: 'Crypto instruments',
      actual: groupCounts['Crypto'] ?? 0,
      expected: 35,
    );

    _assertCount(
      label: 'Indices instruments',
      actual: groupCounts['Indices'] ?? 0,
      expected: 17,
    );

    _assertCount(
      label: 'Shares instruments',
      actual: groupCounts['Shares'] ?? 0,
      expected: 16,
    );

    _assertCount(
      label: 'Reference symbols',
      actual: groupCounts['RefSymbols'] ?? 0,
      expected: 4,
    );

    _assertCount(
      label: 'Full trade mode',
      actual: fullTradeMode,
      expected: 202,
    );

    _assertCount(label: 'Disabled trade mode', actual: disabled, expected: 4);

    _assertCount(
      label: 'Close-only trade mode',
      actual: closeOnly,
      expected: 1,
    );

    _assertCount(
      label: 'New-order allowed',
      actual: newOrderAllowed,
      expected: 202,
    );

    _assertCount(
      label: 'New-order blocked',
      actual: newOrderBlocked,
      expected: 5,
    );

    _assertCount(label: 'Reference-only', actual: referenceOnly, expected: 4);

    final btcUsd = _findInstrument(instruments, 'BTCUSD');

    if (!btcUsd.referenceOnly ||
        !btcUsd.isDisabled ||
        btcUsd.newOrderAllowed ||
        btcUsd.canOpenNewOrders) {
      throw StateError(
        'BTCUSD reference-symbol safety '
        'metadata is incorrect.',
      );
    }

    final tonUsdt = _findInstrument(instruments, 'TONUSDT');

    if (!tonUsdt.isCloseOnly ||
        tonUsdt.newOrderAllowed ||
        tonUsdt.canOpenNewOrders) {
      throw StateError(
        'TONUSDT close-only safety '
        'metadata is incorrect.',
      );
    }

    stdout.writeln();

    stdout.writeln('BTCUSD:');
    stdout.writeln('  group = ${btcUsd.brokerGroup}');
    stdout.writeln(
      '  availability = '
      '${btcUsd.availabilityLabel}',
    );

    stdout.writeln();

    stdout.writeln('TONUSDT:');
    stdout.writeln('  group = ${tonUsdt.brokerGroup}');
    stdout.writeln(
      '  availability = '
      '${tonUsdt.availabilityLabel}',
    );

    stdout.writeln();

    stdout.writeln('DART LIVE PXBT INSTRUMENT CATALOGUE CONFIRMED');
  } finally {
    agentApi.close();
  }
}

void _assertCount({
  required String label,
  required int actual,
  required int expected,
}) {
  if (actual != expected) {
    throw StateError(
      '$label mismatch: '
      'expected $expected, got $actual.',
    );
  }
}

Mt5Instrument _findInstrument(List<Mt5Instrument> instruments, String symbol) {
  for (final instrument in instruments) {
    if (instrument.brokerSymbol == symbol) {
      return instrument;
    }
  }

  throw StateError(
    'Expected instrument $symbol '
    'was not found.',
  );
}
