import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/core/models/mt5_candle.dart';
import 'package:trade_command_center/features/markets/presentation/widgets/market_price_chart.dart';

void main() {
  group('MarketPriceChart', () {
    testWidgets('renders historical candles using the requested height', (
      tester,
    ) async {
      final candles = [
        Mt5Candle(
          barTime: DateTime.parse('2026-08-20T19:59:00Z'),
          open: 1.09980,
          high: 1.10010,
          low: 1.09970,
          close: 1.10000,
          tickVolume: 120,
          spread: 20,
          realVolume: 0,
        ),
        Mt5Candle(
          barTime: DateTime.parse('2026-08-20T20:00:00Z'),
          open: 1.10000,
          high: 1.10030,
          low: 1.09990,
          close: 1.10020,
          tickVolume: 143,
          spread: 20,
          realVolume: 0,
        ),
      ];

      await tester.pumpWidget(
        _testApp(MarketPriceChart(candles: candles, digits: 5, height: 240)),
      );

      await tester.pump();

      expect(find.byKey(const Key('market-price-chart')), findsOneWidget);

      expect(find.byKey(const Key('market-price-chart-empty')), findsNothing);

      expect(
        find.text('No historical candles available for this timeframe.'),
        findsNothing,
      );

      final chart = tester.widget<SizedBox>(
        find.byKey(const Key('market-price-chart')),
      );

      expect(chart.height, 240);

      expect(tester.takeException(), isNull);
    });

    testWidgets('renders safe empty-history state', (tester) async {
      await tester.pumpWidget(
        _testApp(
          const MarketPriceChart(
            candles: <Mt5Candle>[],
            digits: 5,
            height: 220,
          ),
        ),
      );

      await tester.pump();

      expect(find.byKey(const Key('market-price-chart')), findsNothing);

      expect(find.byKey(const Key('market-price-chart-empty')), findsOneWidget);

      expect(
        find.text('No historical candles available for this timeframe.'),
        findsOneWidget,
      );

      final emptyState = tester.widget<Container>(
        find.byKey(const Key('market-price-chart-empty')),
      );

      expect(emptyState.constraints?.maxHeight, 220);

      expect(tester.takeException(), isNull);
    });
  });
}

Widget _testApp(Widget child) {
  return MaterialApp(
    theme: ThemeData.dark(useMaterial3: true),
    home: Scaffold(
      body: Center(child: SizedBox(width: 900, child: child)),
    ),
  );
}
