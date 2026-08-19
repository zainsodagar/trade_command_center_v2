import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/app/app.dart';
import 'package:trade_command_center/features/shell/presentation/widgets/top_bar.dart';

import 'support/dashboard_test_support.dart';

void main() {
  testWidgets(
    'navigation rail stays compact below desktop extension breakpoint',
    (tester) async {
      tester.view.physicalSize = const Size(1000, 800);
      tester.view.devicePixelRatio = 1.0;

      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(
        TradeCommandCenterApp(
          dashboardStatusLoader: buildSafeDashboardLoader(),
        ),
      );

      await tester.pumpAndSettle();

      final rail = tester.widget<NavigationRail>(find.byType(NavigationRail));

      expect(rail.extended, isFalse);

      expect(rail.labelType, NavigationRailLabelType.all);

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

  testWidgets('navigation rail extends on wide desktop windows', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1400, 900);
    tester.view.devicePixelRatio = 1.0;

    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      TradeCommandCenterApp(dashboardStatusLoader: buildSafeDashboardLoader()),
    );

    await tester.pumpAndSettle();

    final rail = tester.widget<NavigationRail>(find.byType(NavigationRail));

    expect(rail.extended, isTrue);

    expect(rail.labelType, NavigationRailLabelType.none);

    expect(find.text('Dashboard'), findsWidgets);

    expect(find.text('Markets'), findsOneWidget);

    expect(find.text('Account'), findsOneWidget);

    expect(find.text('Settings'), findsOneWidget);

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
}
