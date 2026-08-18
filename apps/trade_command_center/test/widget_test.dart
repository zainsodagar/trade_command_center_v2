import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/app/app.dart';

void main() {
  testWidgets('Trade Command Center shell renders in demo read-only mode', (
    tester,
  ) async {
    await tester.pumpWidget(const TradeCommandCenterApp());

    expect(find.text('Trade Command Center'), findsOneWidget);

    expect(find.text('DEMO'), findsOneWidget);

    expect(find.text('READ ONLY'), findsOneWidget);

    expect(find.text('Execution'), findsOneWidget);

    expect(find.text('Disabled'), findsOneWidget);
  });

  testWidgets('navigation switches to account view', (tester) async {
    await tester.pumpWidget(const TradeCommandCenterApp());

    await tester.tap(find.byIcon(Icons.account_balance_wallet_outlined));

    await tester.pumpAndSettle();

    expect(find.text('Account Overview'), findsOneWidget);

    expect(find.text('READ ONLY'), findsOneWidget);
  });
}
