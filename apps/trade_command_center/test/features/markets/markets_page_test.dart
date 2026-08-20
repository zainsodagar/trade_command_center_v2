import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/features/markets/domain/instrument_catalog.dart';
import 'package:trade_command_center/features/markets/presentation/markets_page.dart';

import '../../support/markets_test_support.dart';

void main() {
  group('MarketsPage', () {
    testWidgets('shows initial catalogue loading state', (tester) async {
      final completer = Completer<InstrumentCatalog>();

      final loader = FakeInstrumentCatalogLoader(
        onLoad: () => completer.future,
      );

      await tester.pumpWidget(_testApp(loader));

      await tester.pump();

      expect(find.text('Loading instrument catalogue'), findsOneWidget);

      expect(find.byType(LinearProgressIndicator), findsOneWidget);

      expect(loader.loadCount, 1);

      completer.complete(buildInstrumentCatalog());

      await tester.pumpAndSettle();
    });

    testWidgets('displays loaded catalogue summary and instruments', (
      tester,
    ) async {
      final loader = buildSafeInstrumentCatalogLoader();

      await tester.pumpWidget(_testApp(loader));

      await tester.pumpAndSettle();

      expect(find.text('PXBT MT5 instrument catalogue'), findsOneWidget);

      expect(find.text('Total Instruments'), findsOneWidget);

      expect(find.text('New Orders Available'), findsOneWidget);

      expect(find.text('New Orders Blocked'), findsOneWidget);

      expect(find.text('Reference Only'), findsOneWidget);

      expect(find.text('Showing 7 of 7'), findsOneWidget);

      expect(find.text('EURUSD'), findsOneWidget);

      expect(find.text('AAPL'), findsOneWidget);

      expect(find.text('BTCUSDT'), findsOneWidget);

      expect(find.text('BTCUSD'), findsOneWidget);

      expect(find.text('TONUSDT'), findsOneWidget);

      expect(find.text('BRENT'), findsOneWidget);

      expect(find.text('AUS200'), findsOneWidget);
    });

    testWidgets('shows initial error and retries successfully', (tester) async {
      var attempt = 0;

      final loader = FakeInstrumentCatalogLoader(
        onLoad: () async {
          attempt += 1;

          if (attempt == 1) {
            throw StateError('Agent unavailable');
          }

          return buildInstrumentCatalog();
        },
      );

      await tester.pumpWidget(_testApp(loader));

      await tester.pumpAndSettle();

      expect(find.text('Instrument connection error'), findsOneWidget);

      expect(find.text('Retry'), findsOneWidget);

      await tester.tap(find.text('Retry'));

      await tester.pumpAndSettle();

      expect(find.text('Instrument browser'), findsOneWidget);

      expect(find.text('Showing 7 of 7'), findsOneWidget);

      expect(loader.loadCount, 2);
    });

    testWidgets('searches catalogue by instrument description', (tester) async {
      final loader = buildSafeInstrumentCatalogLoader();

      await tester.pumpWidget(_testApp(loader));

      await tester.pumpAndSettle();

      final search = find.byKey(const Key('markets-search'));

      expect(search, findsOneWidget);

      await tester.enterText(search, 'apple');

      await tester.pumpAndSettle();

      expect(find.text('Showing 1 of 7'), findsOneWidget);

      expect(find.text('AAPL'), findsOneWidget);

      expect(find.text('EURUSD'), findsNothing);
    });

    testWidgets('filters dynamically by broker group', (tester) async {
      final loader = buildSafeInstrumentCatalogLoader();

      await tester.pumpWidget(_testApp(loader));

      await tester.pumpAndSettle();

      final cryptoChip = find.byKey(const ValueKey('markets-group-Crypto'));

      await tester.ensureVisible(cryptoChip);

      await tester.tap(cryptoChip);

      await tester.pumpAndSettle();

      expect(find.text('Showing 2 of 7'), findsOneWidget);

      expect(find.text('BTCUSDT'), findsOneWidget);

      expect(find.text('TONUSDT'), findsOneWidget);

      expect(find.text('AAPL'), findsNothing);
    });

    testWidgets('filters blocked reference-only and close-only instruments', (
      tester,
    ) async {
      final loader = buildSafeInstrumentCatalogLoader();

      await tester.pumpWidget(_testApp(loader));

      await tester.pumpAndSettle();

      final blockedChip = find.byKey(
        const ValueKey('markets-availability-newOrdersBlocked'),
      );

      await tester.ensureVisible(blockedChip);

      await tester.tap(blockedChip);

      await tester.pumpAndSettle();

      expect(find.text('Showing 2 of 7'), findsOneWidget);

      expect(find.text('BTCUSD'), findsOneWidget);

      expect(find.text('TONUSDT'), findsOneWidget);

      expect(find.text('AAPL'), findsNothing);

      final referenceChip = find.byKey(
        const ValueKey('markets-availability-referenceOnly'),
      );

      await tester.ensureVisible(referenceChip);

      await tester.tap(referenceChip);

      await tester.pumpAndSettle();

      expect(find.text('Showing 1 of 7'), findsOneWidget);

      expect(find.text('BTCUSD'), findsOneWidget);

      expect(find.text('Reference only'), findsWidgets);

      expect(find.text('TONUSDT'), findsNothing);

      final closeOnlyChip = find.byKey(
        const ValueKey('markets-availability-closeOnly'),
      );

      await tester.ensureVisible(closeOnlyChip);

      await tester.tap(closeOnlyChip);

      await tester.pumpAndSettle();

      expect(find.text('Showing 1 of 7'), findsOneWidget);

      expect(find.text('TONUSDT'), findsOneWidget);

      expect(find.text('Close only'), findsWidgets);

      expect(find.text('BTCUSD'), findsNothing);
    });

    testWidgets('loads quote and M1 candles when instrument is selected', (
      tester,
    ) async {
      final catalogLoader = buildSafeInstrumentCatalogLoader();
      final marketDataLoader = buildSafeMarketDataLoader();

      await tester.pumpWidget(
        _testApp(catalogLoader, marketDataLoader: marketDataLoader),
      );

      await tester.pumpAndSettle();

      expect(marketDataLoader.quoteLoadCount, 0);
      expect(marketDataLoader.candleLoadCount, 0);

      final btcUsdt = find.byKey(const ValueKey('instrument-BTCUSDT'));

      expect(btcUsdt, findsOneWidget);

      await tester.ensureVisible(btcUsdt);
      await tester.tap(btcUsdt);

      await tester.pumpAndSettle();

      expect(marketDataLoader.quoteLoadCount, 1);
      expect(marketDataLoader.candleLoadCount, 1);

      expect(marketDataLoader.lastQuoteSymbol, 'BTCUSDT');

      expect(marketDataLoader.lastCandleSymbol, 'BTCUSDT');

      expect(marketDataLoader.lastTimeframe, 'M1');

      expect(marketDataLoader.lastCount, 100);

      expect(
        find.byKey(const Key('markets-selected-market-data')),
        findsOneWidget,
      );

      expect(find.text('BTCUSDT market data'), findsOneWidget);

      expect(
        find.text('Read-only live quote and M1 historical candles loaded.'),
        findsOneWidget,
      );
    });

    testWidgets('displays typed quote and candle values', (tester) async {
      final catalogLoader = buildSafeInstrumentCatalogLoader();
      final marketDataLoader = buildSafeMarketDataLoader();

      await tester.pumpWidget(
        _testApp(catalogLoader, marketDataLoader: marketDataLoader),
      );

      await tester.pumpAndSettle();

      final btcUsdt = find.byKey(const ValueKey('instrument-BTCUSDT'));

      await tester.ensureVisible(btcUsdt);
      await tester.tap(btcUsdt);
      await tester.pumpAndSettle();

      String marketValue(String label) {
        final textWidget = tester.widget<Text>(
          find.byKey(ValueKey('market-data-$label')),
        );

        return textWidget.data ?? '';
      }

      expect(marketValue('Bid'), '1.10000');

      expect(marketValue('Ask'), '1.10020');

      expect(marketValue('Spread'), '0.00020');

      expect(marketValue('Spread Points'), '20.00');

      expect(marketValue('Tick Time'), '2026-08-20T20:00:15.000Z');

      expect(marketValue('Quote Status'), 'Available');

      expect(marketValue('Timeframe'), 'M1');

      expect(marketValue('Candle Count'), '2');

      expect(marketValue('Oldest Candle'), '2026-08-20T19:59:00.000Z');

      expect(marketValue('Latest Candle'), '2026-08-20T20:00:00.000Z');

      expect(marketValue('History Status'), 'Available');

      expect(
        find.byKey(const Key('market-price-chart')),
        findsOneWidget,
        reason: 'Normal history must render the candlestick chart.',
      );

      expect(find.byKey(const Key('market-price-chart-empty')), findsNothing);
    });

    testWidgets('displays safe stale-history state', (tester) async {
      final catalogLoader = buildSafeInstrumentCatalogLoader();

      final marketDataLoader = FakeMarketDataLoader(
        onLoadQuote: (brokerSymbol) async {
          return buildMarketQuote(brokerSymbol: brokerSymbol);
        },
        onLoadCandles:
            ({
              required brokerSymbol,
              required timeframe,
              required count,
            }) async {
              return buildMarketCandleSeries(
                brokerSymbol: brokerSymbol,
                timeframe: timeframe,
                countRequested: count,
                available: false,
                unavailableReason: 'history_stale',
              );
            },
      );

      await tester.pumpWidget(
        _testApp(catalogLoader, marketDataLoader: marketDataLoader),
      );

      await tester.pumpAndSettle();

      final eurUsd = find.byKey(const ValueKey('instrument-EURUSD'));

      await tester.ensureVisible(eurUsd);
      await tester.tap(eurUsd);
      await tester.pumpAndSettle();

      String marketValue(String label) {
        final textWidget = tester.widget<Text>(
          find.byKey(ValueKey('market-data-$label')),
        );

        return textWidget.data ?? '';
      }

      expect(marketValue('Quote Status'), 'Available');

      expect(marketValue('Timeframe'), 'M1');

      expect(marketValue('Candle Count'), '0');

      expect(marketValue('Oldest Candle'), 'Unavailable');

      expect(marketValue('Latest Candle'), 'Unavailable');

      expect(marketValue('History Status'), 'history_stale');

      expect(
        find.text('Read-only live quote and M1 historical candles loaded.'),
        findsOneWidget,
      );

      expect(
        find.textContaining('Unable to load read-only quote'),
        findsNothing,
      );

      expect(find.byKey(const Key('market-price-chart')), findsNothing);

      expect(
        find.byKey(const Key('market-price-chart-empty')),
        findsOneWidget,
        reason: 'history_stale must render the safe empty chart state.',
      );

      expect(
        find.text('No historical candles available for this timeframe.'),
        findsOneWidget,
      );
    });

    testWidgets('changing timeframe reloads candles without reloading quote', (
      tester,
    ) async {
      final catalogLoader = buildSafeInstrumentCatalogLoader();
      final marketDataLoader = buildSafeMarketDataLoader();

      await tester.pumpWidget(
        _testApp(catalogLoader, marketDataLoader: marketDataLoader),
      );

      await tester.pumpAndSettle();

      final btcUsdt = find.byKey(const ValueKey('instrument-BTCUSDT'));

      expect(btcUsdt, findsOneWidget);

      await tester.ensureVisible(btcUsdt);
      await tester.tap(btcUsdt);
      await tester.pumpAndSettle();

      expect(marketDataLoader.quoteLoadCount, 1);

      expect(marketDataLoader.candleLoadCount, 1);

      expect(marketDataLoader.lastQuoteSymbol, 'BTCUSDT');

      expect(marketDataLoader.lastCandleSymbol, 'BTCUSDT');

      expect(marketDataLoader.lastTimeframe, 'M1');

      expect(marketDataLoader.lastCount, 100);

      final h4Chip = find.byKey(const ValueKey('markets-timeframe-H4'));

      expect(h4Chip, findsOneWidget);

      await tester.ensureVisible(h4Chip);
      await tester.tap(h4Chip);
      await tester.pumpAndSettle();

      expect(
        marketDataLoader.quoteLoadCount,
        1,
        reason: 'Changing timeframe must not reload the quote.',
      );

      expect(
        marketDataLoader.candleLoadCount,
        2,
        reason: 'Changing timeframe must load a new candle series.',
      );

      expect(marketDataLoader.lastQuoteSymbol, 'BTCUSDT');

      expect(marketDataLoader.lastCandleSymbol, 'BTCUSDT');

      expect(marketDataLoader.lastTimeframe, 'H4');

      expect(marketDataLoader.lastCount, 100);

      final timeframeValue = tester.widget<Text>(
        find.byKey(const ValueKey('market-data-Timeframe')),
      );

      expect(timeframeValue.data, 'H4');

      expect(
        find.text('Read-only live quote and H4 historical candles loaded.'),
        findsOneWidget,
      );

      final h4ChoiceChip = tester.widget<ChoiceChip>(h4Chip);

      expect(h4ChoiceChip.selected, isTrue);
    });

    testWidgets('selecting a new instrument resets timeframe to M1', (
      tester,
    ) async {
      final catalogLoader = buildSafeInstrumentCatalogLoader();
      final marketDataLoader = buildSafeMarketDataLoader();

      await tester.pumpWidget(
        _testApp(catalogLoader, marketDataLoader: marketDataLoader),
      );

      await tester.pumpAndSettle();

      final btcUsdt = find.byKey(const ValueKey('instrument-BTCUSDT'));

      await tester.ensureVisible(btcUsdt);
      await tester.tap(btcUsdt);
      await tester.pumpAndSettle();

      expect(marketDataLoader.quoteLoadCount, 1);

      expect(marketDataLoader.candleLoadCount, 1);

      expect(marketDataLoader.lastTimeframe, 'M1');

      final h1Chip = find.byKey(const ValueKey('markets-timeframe-H1'));

      expect(h1Chip, findsOneWidget);

      await tester.ensureVisible(h1Chip);
      await tester.tap(h1Chip);
      await tester.pumpAndSettle();

      expect(
        marketDataLoader.quoteLoadCount,
        1,
        reason: 'Changing timeframe must not reload the quote.',
      );

      expect(marketDataLoader.candleLoadCount, 2);

      expect(marketDataLoader.lastTimeframe, 'H1');

      final h1Selected = tester.widget<ChoiceChip>(h1Chip);

      expect(h1Selected.selected, isTrue);

      final eurUsd = find.byKey(const ValueKey('instrument-EURUSD'));

      expect(eurUsd, findsOneWidget);

      await tester.ensureVisible(eurUsd);
      await tester.tap(eurUsd);
      await tester.pumpAndSettle();

      expect(
        marketDataLoader.quoteLoadCount,
        2,
        reason: 'Selecting a different instrument must load its quote.',
      );

      expect(
        marketDataLoader.candleLoadCount,
        3,
        reason:
            'Selecting a different instrument must load its initial history.',
      );

      expect(marketDataLoader.lastQuoteSymbol, 'EURUSD');

      expect(marketDataLoader.lastCandleSymbol, 'EURUSD');

      expect(
        marketDataLoader.lastTimeframe,
        'M1',
        reason: 'Every newly selected instrument must start at M1.',
      );

      expect(marketDataLoader.lastCount, 100);

      final m1Chip = find.byKey(const ValueKey('markets-timeframe-M1'));

      final currentH1Chip = find.byKey(const ValueKey('markets-timeframe-H1'));

      expect(m1Chip, findsOneWidget);
      expect(currentH1Chip, findsOneWidget);

      final m1Selected = tester.widget<ChoiceChip>(m1Chip);

      final h1NotSelected = tester.widget<ChoiceChip>(currentH1Chip);

      expect(m1Selected.selected, isTrue);

      expect(h1NotSelected.selected, isFalse);

      final timeframeValue = tester.widget<Text>(
        find.byKey(const ValueKey('market-data-Timeframe')),
      );

      expect(timeframeValue.data, 'M1');

      expect(
        find.text('Read-only live quote and M1 historical candles loaded.'),
        findsOneWidget,
      );
    });

    testWidgets('failed refresh preserves last successful catalogue', (
      tester,
    ) async {
      var attempt = 0;

      final loader = FakeInstrumentCatalogLoader(
        onLoad: () async {
          attempt += 1;

          if (attempt == 1) {
            return buildInstrumentCatalog();
          }

          throw StateError('Refresh unavailable');
        },
      );

      await tester.pumpWidget(_testApp(loader));

      await tester.pumpAndSettle();

      expect(find.text('Showing 7 of 7'), findsOneWidget);

      final refresh = find.byKey(const Key('markets-refresh'));

      await tester.tap(refresh);

      await tester.pumpAndSettle();

      expect(find.text('Refresh failed'), findsOneWidget);

      expect(find.text('Showing 7 of 7'), findsOneWidget);

      expect(find.text('BTCUSDT'), findsOneWidget);

      expect(loader.loadCount, 2);
    });
  });
}

Widget _testApp(
  FakeInstrumentCatalogLoader loader, {
  FakeMarketDataLoader? marketDataLoader,
}) {
  return MaterialApp(
    theme: ThemeData.dark(useMaterial3: true),
    home: Scaffold(
      body: MarketsPage(
        catalogLoader: loader,
        marketDataLoader: marketDataLoader,
      ),
    ),
  );
}
