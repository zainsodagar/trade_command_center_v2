import 'package:flutter/material.dart';

import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/page_frame.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PageFrame(
      title: 'Settings',
      subtitle: 'Local connection, display, and application preferences.',
      icon: Icons.settings_outlined,
      child: EmptyState(
        title: 'Settings foundation ready',
        message:
            'Connection and display configuration will be added '
            'without storing broker credentials in the Flutter app.',
        icon: Icons.tune,
      ),
    );
  }
}
