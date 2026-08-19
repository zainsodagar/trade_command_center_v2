import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/features/dashboard/domain/dashboard_status.dart';
import 'package:trade_command_center/features/dashboard/presentation/dashboard_page.dart';

import '../../support/dashboard_test_support.dart';

void main() {
  group('DashboardPage', () {
    testWidgets('shows loading state while local services are being read', (
      tester,
    ) async {
      final completer = Completer<DashboardStatus>();

      final loader = FakeDashboardStatusLoader(onLoad: () => completer.future);

      await _pumpDashboard(tester, loader);

      expect(find.text('Loading local services'), findsOneWidget);

      expect(find.text('Refreshing...'), findsOneWidget);

      expect(find.byType(LinearProgressIndicator), findsOneWidget);

      expect(loader.loadCount, 1);

      completer.complete(buildDashboardStatus());

      await tester.pumpAndSettle();

      expect(find.text('Connected — read-only safe'), findsOneWidget);
    });

    testWidgets('shows connected read-only safe status', (tester) async {
      final loader = buildSafeDashboardLoader();

      await _pumpDashboard(tester, loader);

      await tester.pumpAndSettle();

      expect(find.text('Connected — read-only safe'), findsOneWidget);

      expect(find.text('Online'), findsOneWidget);

      expect(find.text('Connected'), findsOneWidget);

      expect(find.text('DEMO'), findsOneWidget);

      expect(find.text('***7959'), findsOneWidget);

      expect(find.text('PXBTTrading-1'), findsOneWidget);

      expect(find.text('USD'), findsOneWidget);

      expect(find.text('1:100'), findsOneWidget);

      expect(find.text('Read-only safe'), findsOneWidget);

      expect(loader.loadCount, 1);
    });

    testWidgets('shows connection error when initial load fails', (
      tester,
    ) async {
      final loader = FakeDashboardStatusLoader(
        onLoad: () async {
          throw StateError('Local service unavailable');
        },
      );

      await _pumpDashboard(tester, loader);

      await tester.pumpAndSettle();

      expect(find.text('Connection error'), findsOneWidget);

      expect(find.textContaining('Local service unavailable'), findsOneWidget);

      expect(find.text('Connected — read-only safe'), findsNothing);

      expect(loader.loadCount, 1);
    });

    testWidgets('shows unsafe state when any execution layer is enabled', (
      tester,
    ) async {
      final loader = FakeDashboardStatusLoader(
        onLoad: () async {
          return buildDashboardStatus(backendExecutionEnabled: true);
        },
      );

      await _pumpDashboard(tester, loader);

      await tester.pumpAndSettle();

      expect(find.text('Attention required'), findsWidgets);

      expect(find.text('Enabled'), findsOneWidget);

      expect(find.text('Connected — read-only safe'), findsNothing);

      expect(loader.loadCount, 1);
    });

    testWidgets('refresh reloads and displays the new status', (tester) async {
      var responseNumber = 0;

      final loader = FakeDashboardStatusLoader(
        onLoad: () async {
          responseNumber += 1;

          if (responseNumber == 1) {
            return buildDashboardStatus();
          }

          return buildDashboardStatus(backendExecutionEnabled: true);
        },
      );

      await _pumpDashboard(tester, loader);

      await tester.pumpAndSettle();

      expect(find.text('Connected — read-only safe'), findsOneWidget);

      expect(loader.loadCount, 1);

      await tester.tap(find.text('Refresh'));

      await tester.pump();

      expect(loader.loadCount, 2);

      await tester.pumpAndSettle();

      expect(find.text('Attention required'), findsWidgets);

      expect(find.text('Enabled'), findsOneWidget);

      expect(find.text('Refresh'), findsOneWidget);
    });

    testWidgets('failed refresh preserves last successful status', (
      tester,
    ) async {
      var responseNumber = 0;

      final loader = FakeDashboardStatusLoader(
        onLoad: () async {
          responseNumber += 1;

          if (responseNumber == 1) {
            return buildDashboardStatus();
          }

          throw StateError('Refresh service failure');
        },
      );

      await _pumpDashboard(tester, loader);

      await tester.pumpAndSettle();

      expect(find.text('Connected — read-only safe'), findsOneWidget);

      await tester.tap(find.text('Refresh'));

      await tester.pump();

      expect(loader.loadCount, 2);

      await tester.pumpAndSettle();

      expect(find.text('Refresh failed'), findsOneWidget);

      expect(find.text('Connected — read-only safe'), findsOneWidget);

      expect(find.text('Online'), findsOneWidget);

      expect(find.text('Connected'), findsOneWidget);

      expect(find.text('Refresh'), findsOneWidget);
    });
  });
}

Future<void> _pumpDashboard(
  WidgetTester tester,
  FakeDashboardStatusLoader loader,
) async {
  tester.view.physicalSize = const Size(1400, 1000);

  tester.view.devicePixelRatio = 1.0;

  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });

  await tester.pumpWidget(
    MaterialApp(
      theme: ThemeData.dark(),
      home: DashboardPage(statusLoader: loader),
    ),
  );
}
