import 'package:flutter/material.dart';

import '../../../core/widgets/empty_state.dart';
import '../../../core/widgets/page_frame.dart';

class MarketsPage extends StatelessWidget {
  const MarketsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const PageFrame(
      title: 'Markets',
      subtitle: 'Dynamic broker instruments, quotes, and market data.',
      icon: Icons.candlestick_chart_outlined,
      child: EmptyState(
        title: 'Market data connection pending',
        message:
            'The validated MT5 instrument, quote, and candle APIs '
            'will be connected in a later checkpoint.',
        icon: Icons.show_chart,
      ),
    );
  }
}
