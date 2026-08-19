import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:trade_command_center/features/markets/presentation/markets_page.dart';

import '../../support/markets_test_support.dart';

void main() {
  testWidgets(
    'search input preserves text direction and cursor position across rebuilds',
    (tester) async {
      final loader = buildSafeInstrumentCatalogLoader();

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(useMaterial3: true),
          home: Scaffold(body: MarketsPage(catalogLoader: loader)),
        ),
      );

      await tester.pumpAndSettle();

      final search = find.byKey(const Key('markets-search'));

      await tester.tap(search);

      await tester.enterText(search, 'gold');

      await tester.pump();

      EditableText editable = tester.widget<EditableText>(
        find.descendant(of: search, matching: find.byType(EditableText)),
      );

      expect(editable.controller.text, 'gold');

      expect(editable.controller.selection.extentOffset, 4);

      tester.testTextInput.updateEditingValue(
        const TextEditingValue(
          text: 'gol',
          selection: TextSelection.collapsed(offset: 3),
        ),
      );

      await tester.pump();

      editable = tester.widget<EditableText>(
        find.descendant(of: search, matching: find.byType(EditableText)),
      );

      expect(editable.controller.text, 'gol');

      expect(editable.controller.selection.extentOffset, 3);

      tester.testTextInput.updateEditingValue(
        const TextEditingValue(
          text: 'gold',
          selection: TextSelection.collapsed(offset: 4),
        ),
      );

      await tester.pump();

      editable = tester.widget<EditableText>(
        find.descendant(of: search, matching: find.byType(EditableText)),
      );

      expect(editable.controller.text, 'gold');

      expect(editable.controller.selection.extentOffset, 4);
    },
  );
}
