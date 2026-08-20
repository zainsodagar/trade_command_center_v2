import 'dart:io';

import 'package:trade_command_center/core/services/agent_api.dart';

Future<void> main(List<String> args) async {
  if (args.length != 3) {
    stderr.writeln(
      'Usage: dart run tool/live_market_data_probe.dart '
      '<broker_symbol> <timeframe> <count>',
    );

    exitCode = 64;
    return;
  }

  final brokerSymbol = args[0];
  final timeframe = args[1];

  final count = int.tryParse(args[2]);

  if (count == null || count < 1) {
    stderr.writeln('Count must be a positive integer.');

    exitCode = 64;
    return;
  }

  final agentApi = AgentApi();

  try {
    stdout.writeln('TCC LIVE MT5 MARKET DATA PROBE');
    stdout.writeln();

    final quote = await agentApi.getMt5Quote(brokerSymbol);

    stdout.writeln('Quote:');
    stdout.writeln('  symbol = ${quote.brokerSymbol}');
    stdout.writeln('  available = ${quote.quoteAvailable}');
    stdout.writeln('  tickTime = ${quote.tickTime}');
    stdout.writeln('  bid = ${quote.bid}');
    stdout.writeln('  ask = ${quote.ask}');
    stdout.writeln('  spread = ${quote.spread}');
    stdout.writeln(
      '  unavailableReason = '
      '${quote.unavailableReason}',
    );

    if (quote.brokerSymbol != brokerSymbol) {
      throw StateError(
        'Quote symbol mismatch: expected '
        '$brokerSymbol, got ${quote.brokerSymbol}.',
      );
    }

    stdout.writeln();

    final stopwatch = Stopwatch()..start();

    final series = await agentApi.getMt5Candles(
      brokerSymbol: brokerSymbol,
      timeframe: timeframe,
      count: count,
    );

    stopwatch.stop();

    stdout.writeln('Candles:');
    stdout.writeln('  symbol = ${series.brokerSymbol}');
    stdout.writeln('  timeframe = ${series.timeframe}');
    stdout.writeln(
      '  countRequested = '
      '${series.countRequested}',
    );
    stdout.writeln(
      '  available = '
      '${series.candlesAvailable}',
    );
    stdout.writeln('  candleCount = ${series.candleCount}');
    stdout.writeln('  oldest = ${series.oldestCandleTime}');
    stdout.writeln('  latest = ${series.latestCandleTime}');
    stdout.writeln(
      '  unavailableReason = '
      '${series.unavailableReason}',
    );
    stdout.writeln(
      '  requestMilliseconds = '
      '${stopwatch.elapsedMilliseconds}',
    );

    if (series.brokerSymbol != brokerSymbol) {
      throw StateError(
        'Candle symbol mismatch: expected '
        '$brokerSymbol, got ${series.brokerSymbol}.',
      );
    }

    if (series.timeframe != timeframe) {
      throw StateError(
        'Timeframe mismatch: expected '
        '$timeframe, got ${series.timeframe}.',
      );
    }

    if (series.countRequested != count) {
      throw StateError(
        'Requested count mismatch: expected '
        '$count, got ${series.countRequested}.',
      );
    }

    if (series.candlesAvailable) {
      if (series.candleCount != series.candles.length) {
        throw StateError(
          'Candle count does not match parsed '
          'candle list length.',
        );
      }

      if (series.candles.isEmpty) {
        throw StateError(
          'Candles are marked available but '
          'the parsed candle list is empty.',
        );
      }

      if (series.latestCandleTime == null) {
        throw StateError(
          'Available candle history has no '
          'latest candle time.',
        );
      }

      if (quote.quoteAvailable && quote.tickTime != null) {
        final gap = quote.tickTime!.difference(series.latestCandleTime!);

        stdout.writeln(
          '  quoteToLatestGapSeconds = '
          '${gap.inSeconds}',
        );
      }
    } else {
      if (series.candles.isNotEmpty) {
        throw StateError(
          'Unavailable candle history must not '
          'contain candle data.',
        );
      }

      if (series.unavailableReason == null) {
        throw StateError(
          'Unavailable candle history must '
          'provide a reason.',
        );
      }
    }

    stdout.writeln();
    stdout.writeln('DART LIVE MT5 MARKET DATA CONFIRMED');
  } finally {
    agentApi.close();
  }
}
