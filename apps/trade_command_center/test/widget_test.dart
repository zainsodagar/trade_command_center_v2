import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/app/app.dart';

void main() {
  testWidgets('desktop shell starts on dashboard in demo read-only mode', (
    tester,
  ) async {
    await tester.pumpWidget(const TradeCommandCenterApp());

    expect(find.text('Trade Command Center'), findsOneWidget);

    expect(find.text('DEMO'), findsOneWidget);

    expect(find.text('READ ONLY'), findsOneWidget);

    expect(find.text('Backend'), findsOneWidget);

    expect(find.text('MT5 Agent'), findsOneWidget);

    expect(find.text('Account Mode'), findsOneWidget);

    expect(find.text('Execution'), findsOneWidget);

    expect(find.text('Disabled'), findsOneWidget);
  });

  testWidgets('navigation opens markets view', (tester) async {
    await tester.pumpWidget(const TradeCommandCenterApp());

    await tester.tap(find.byIcon(Icons.candlestick_chart_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Market data connection pending'), findsOneWidget);

    expect(find.text('DEMO'), findsOneWidget);

    expect(find.text('READ ONLY'), findsOneWidget);
  });

  testWidgets('navigation opens account view', (tester) async {
    await tester.pumpWidget(const TradeCommandCenterApp());

    await tester.tap(find.byIcon(Icons.account_balance_wallet_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Account Overview'), findsOneWidget);

    expect(find.text('Demo account connection pending'), findsOneWidget);

    expect(find.text('DEMO'), findsOneWidget);

    expect(find.text('READ ONLY'), findsOneWidget);
  });

  testWidgets('navigation opens settings view', (tester) async {
    await tester.pumpWidget(const TradeCommandCenterApp());

    await tester.tap(find.byIcon(Icons.settings_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Settings foundation ready'), findsOneWidget);

    expect(find.text('DEMO'), findsOneWidget);

    expect(find.text('READ ONLY'), findsOneWidget);
  });

  testWidgets(
    'navigation can return to dashboard with safety state preserved',
    (tester) async {
      await tester.pumpWidget(const TradeCommandCenterApp());

      await tester.tap(find.byIcon(Icons.candlestick_chart_outlined));

      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.dashboard_outlined));

      await tester.pumpAndSettle();

      expect(find.text('Backend'), findsOneWidget);

      expect(find.text('Execution'), findsOneWidget);

      expect(find.text('Disabled'), findsOneWidget);

      expect(find.text('DEMO'), findsOneWidget);

      expect(find.text('READ ONLY'), findsOneWidget);
    },
  );
}
