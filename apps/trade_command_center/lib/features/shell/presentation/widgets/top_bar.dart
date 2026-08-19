import 'package:flutter/material.dart';

import 'status_badge.dart';

class TopBar extends StatelessWidget {
  const TopBar({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      child: Row(
        children: [
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Trade Command Center',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                ),
                SizedBox(height: 2),
                Text(
                  'Windows Desktop',
                  style: TextStyle(fontSize: 12, color: Colors.white54),
                ),
              ],
            ),
          ),
          const StatusBadge(label: 'DEMO', icon: Icons.science_outlined),
          const SizedBox(width: 8),
          const StatusBadge(
            label: 'READ ONLY',
            icon: Icons.lock_outline,
            emphasized: true,
          ),
        ],
      ),
    );
  }
}
