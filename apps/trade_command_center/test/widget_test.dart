import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/app/app.dart';
import 'package:trade_command_center/features/shell/presentation/widgets/top_bar.dart';

import 'support/dashboard_test_support.dart';

void main() {
  testWidgets('desktop shell starts on dashboard in demo read-only mode', (
    tester,
  ) async {
    await tester.pumpWidget(
      TradeCommandCenterApp(dashboardStatusLoader: buildSafeDashboardLoader()),
    );

    await tester.pumpAndSettle();

    expect(find.text('Trade Command Center'), findsOneWidget);

    expect(
      find.descendant(of: find.byType(TopBar), matching: find.text('DEMO')),
      findsOneWidget,
    );

    expect(
      find.descendant(
        of: find.byType(TopBar),
        matching: find.text('READ ONLY'),
      ),
      findsOneWidget,
    );

    expect(find.text('Backend'), findsOneWidget);

    expect(find.text('MT5 Agent'), findsOneWidget);

    expect(find.text('Account Mode'), findsOneWidget);

    expect(find.text('Execution'), findsOneWidget);

    expect(find.text('Disabled'), findsWidgets);

    expect(find.text('Connected — read-only safe'), findsOneWidget);
  });

  testWidgets('navigation opens markets view', (tester) async {
    await tester.pumpWidget(
      TradeCommandCenterApp(dashboardStatusLoader: buildSafeDashboardLoader()),
    );

    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.candlestick_chart_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Market data connection pending'), findsOneWidget);

    expect(
      find.descendant(of: find.byType(TopBar), matching: find.text('DEMO')),
      findsOneWidget,
    );

    expect(
      find.descendant(
        of: find.byType(TopBar),
        matching: find.text('READ ONLY'),
      ),
      findsOneWidget,
    );
  });

  testWidgets('navigation opens account view', (tester) async {
    await tester.pumpWidget(
      TradeCommandCenterApp(dashboardStatusLoader: buildSafeDashboardLoader()),
    );

    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.account_balance_wallet_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Account Overview'), findsOneWidget);

    expect(find.text('Demo account connection pending'), findsOneWidget);

    expect(
      find.descendant(of: find.byType(TopBar), matching: find.text('DEMO')),
      findsOneWidget,
    );

    expect(
      find.descendant(
        of: find.byType(TopBar),
        matching: find.text('READ ONLY'),
      ),
      findsOneWidget,
    );
  });

  testWidgets('navigation opens settings view', (tester) async {
    await tester.pumpWidget(
      TradeCommandCenterApp(dashboardStatusLoader: buildSafeDashboardLoader()),
    );

    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.settings_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Settings foundation ready'), findsOneWidget);

    expect(
      find.descendant(of: find.byType(TopBar), matching: find.text('DEMO')),
      findsOneWidget,
    );

    expect(
      find.descendant(
        of: find.byType(TopBar),
        matching: find.text('READ ONLY'),
      ),
      findsOneWidget,
    );
  });

  testWidgets(
    'navigation can return to dashboard with safety state preserved',
    (tester) async {
      await tester.pumpWidget(
        TradeCommandCenterApp(
          dashboardStatusLoader: buildSafeDashboardLoader(),
        ),
      );

      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.candlestick_chart_outlined));

      await tester.pumpAndSettle();

      await tester.tap(find.byIcon(Icons.dashboard_outlined));

      await tester.pumpAndSettle();

      expect(find.text('Backend'), findsOneWidget);

      expect(find.text('Execution'), findsOneWidget);

      expect(find.text('Disabled'), findsWidgets);

      expect(find.text('Connected — read-only safe'), findsOneWidget);

      expect(
        find.descendant(of: find.byType(TopBar), matching: find.text('DEMO')),
        findsOneWidget,
      );

      expect(
        find.descendant(
          of: find.byType(TopBar),
          matching: find.text('READ ONLY'),
        ),
        findsOneWidget,
      );
    },
  );
}
