import 'package:flutter/material.dart';

import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/page_frame.dart';

class AccountPage extends StatelessWidget {
  const AccountPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PageFrame(
      title: 'Account Overview',
      subtitle:
          'Read-only demo account balance, equity, margin, '
          'and risk state.',
      icon: Icons.account_balance_wallet_outlined,
      child: EmptyState(
        title: 'Demo account connection pending',
        message:
            'Validated MT5 demo account metrics will appear here '
            'after API connectivity is introduced.',
        icon: Icons.account_balance_outlined,
      ),
    );
  }
}
