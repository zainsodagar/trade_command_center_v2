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

Widget _testApp(FakeInstrumentCatalogLoader loader) {
  return MaterialApp(
    theme: ThemeData.dark(useMaterial3: true),
    home: Scaffold(body: MarketsPage(catalogLoader: loader)),
  );
}
