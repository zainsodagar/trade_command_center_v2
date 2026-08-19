import 'package:flutter/material.dart';

import '../../../core/models/mt5_instrument.dart';
import '../../../core/widgets/metric_card.dart';
import '../../../core/widgets/page_frame.dart';
import '../data/instrument_catalog_service.dart';
import '../domain/instrument_catalog.dart';
import '../domain/instrument_catalog_loader.dart';

class MarketsPage extends StatefulWidget {
  const MarketsPage({this.catalogLoader, super.key});

  final InstrumentCatalogLoader? catalogLoader;

  @override
  State<MarketsPage> createState() => _MarketsPageState();
}

class _MarketsPageState extends State<MarketsPage> {
  late final InstrumentCatalogLoader _catalogLoader;
  late final bool _ownsCatalogLoader;
  late final TextEditingController _searchController;

  InstrumentCatalog? _catalog;
  Object? _error;

  bool _loading = true;

  String _query = '';
  String? _selectedGroup;

  InstrumentAvailabilityFilter _availability = InstrumentAvailabilityFilter.all;

  @override
  void initState() {
    super.initState();

    _searchController = TextEditingController();

    _ownsCatalogLoader = widget.catalogLoader == null;

    _catalogLoader = widget.catalogLoader ?? InstrumentCatalogService();

    _loadCatalog();
  }

  @override
  void dispose() {
    _searchController.dispose();

    if (_ownsCatalogLoader) {
      _catalogLoader.close();
    }

    super.dispose();
  }

  Future<void> _loadCatalog() async {
    if (mounted) {
      setState(() {
        _loading = true;
        _error = null;
      });
    }

    try {
      final catalog = await _catalogLoader.load();

      if (!mounted) {
        return;
      }

      setState(() {
        _catalog = catalog;
        _loading = false;

        if (_selectedGroup != null &&
            !catalog.brokerGroups.contains(_selectedGroup)) {
          _selectedGroup = null;
        }
      });
    } catch (error) {
      if (!mounted) {
        return;
      }

      setState(() {
        _error = error;
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return PageFrame(
      title: 'Markets',
      subtitle: 'Dynamic PXBT MT5 instruments and read-only market metadata.',
      icon: Icons.candlestick_chart_outlined,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _MarketsHeader(loading: _loading, onRefresh: _loadCatalog),
          const SizedBox(height: 16),
          _buildContent(context),
        ],
      ),
    );
  }

  Widget _buildContent(BuildContext context) {
    final catalog = _catalog;
    final error = _error;

    if (catalog == null && _loading) {
      return const _MarketsStatePanel(
        icon: Icons.sync,
        title: 'Loading instrument catalogue',
        message:
            'Reading the dynamic PXBT MT5 instrument catalogue '
            'through the local Windows execution agent.',
        showProgress: true,
      );
    }

    if (catalog == null && error != null) {
      return _MarketsStatePanel(
        icon: Icons.cloud_off_outlined,
        title: 'Instrument connection error',
        message:
            'Unable to load the PXBT MT5 instrument catalogue.\n\n'
            '$error',
        action: FilledButton.tonalIcon(
          onPressed: _loadCatalog,
          icon: const Icon(Icons.refresh, size: 18),
          label: const Text('Retry'),
        ),
      );
    }

    if (catalog == null) {
      return const _MarketsStatePanel(
        icon: Icons.info_outline,
        title: 'Catalogue unavailable',
        message: 'No broker instrument catalogue is currently available.',
      );
    }

    final filtered = catalog.filter(
      query: _query,
      brokerGroup: _selectedGroup,
      availability: _availability,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (error != null) ...[
          const _MarketsStatePanel(
            icon: Icons.warning_amber_outlined,
            title: 'Refresh failed',
            message:
                'Showing the last successfully loaded instrument '
                'catalogue. Use Refresh to try the local agent again.',
          ),
          const SizedBox(height: 16),
        ],
        if (_loading) ...[
          const LinearProgressIndicator(),
          const SizedBox(height: 16),
        ],
        Wrap(
          spacing: 16,
          runSpacing: 16,
          children: [
            MetricCard(
              label: 'Total Instruments',
              value: '${catalog.totalCount}',
              icon: Icons.list_alt_outlined,
            ),
            MetricCard(
              label: 'New Orders Available',
              value: '${catalog.newOrdersAvailableCount}',
              icon: Icons.check_circle_outline,
            ),
            MetricCard(
              label: 'New Orders Blocked',
              value: '${catalog.newOrdersBlockedCount}',
              icon: Icons.block_outlined,
            ),
            MetricCard(
              label: 'Reference Only',
              value: '${catalog.referenceOnlyCount}',
              icon: Icons.visibility_outlined,
            ),
          ],
        ),
        const SizedBox(height: 24),
        _SearchPanel(
          controller: _searchController,
          onChanged: (value) {
            setState(() {
              _query = value;
            });
          },
        ),
        const SizedBox(height: 20),
        _SectionLabel(
          title: 'Broker groups',
          subtitle:
              '${catalog.brokerGroups.length} groups discovered dynamically',
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ChoiceChip(
              key: const Key('markets-group-all'),
              label: Text('All (${catalog.totalCount})'),
              selected: _selectedGroup == null,
              onSelected: (_) {
                setState(() {
                  _selectedGroup = null;
                });
              },
            ),
            for (final group in catalog.brokerGroups)
              ChoiceChip(
                key: ValueKey('markets-group-$group'),
                label: Text(
                  '$group '
                  '(${catalog.groupCounts[group] ?? 0})',
                ),
                selected: _selectedGroup == group,
                onSelected: (_) {
                  setState(() {
                    _selectedGroup = group;
                  });
                },
              ),
          ],
        ),
        const SizedBox(height: 20),
        const _SectionLabel(
          title: 'Availability',
          subtitle:
              'Read-only broker metadata; no execution controls are exposed.',
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            for (final filter in InstrumentAvailabilityFilter.values)
              ChoiceChip(
                key: ValueKey('markets-availability-${filter.name}'),
                label: Text(_availabilityFilterLabel(filter)),
                selected: _availability == filter,
                onSelected: (_) {
                  setState(() {
                    _availability = filter;
                  });
                },
              ),
          ],
        ),
        const SizedBox(height: 24),
        Row(
          children: [
            Expanded(
              child: Text(
                'Instrument browser',
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
              ),
            ),
            Text(
              'Showing ${filtered.length} '
              'of ${catalog.totalCount}',
              key: const Key('markets-result-count'),
              style: const TextStyle(color: Colors.white60),
            ),
          ],
        ),
        const SizedBox(height: 12),
        if (filtered.isEmpty)
          const _MarketsStatePanel(
            icon: Icons.search_off_outlined,
            title: 'No matching instruments',
            message:
                'Adjust the search text, broker group, '
                'or availability filter.',
          )
        else
          _InstrumentList(instruments: filtered),
      ],
    );
  }
}

class _MarketsHeader extends StatelessWidget {
  const _MarketsHeader({required this.loading, required this.onRefresh});

  final bool loading;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Expanded(
          child: Text(
            'PXBT MT5 instrument catalogue',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
          ),
        ),
        FilledButton.tonalIcon(
          key: const Key('markets-refresh'),
          onPressed: loading ? null : onRefresh,
          icon: const Icon(Icons.refresh, size: 18),
          label: Text(loading ? 'Refreshing...' : 'Refresh'),
        ),
      ],
    );
  }
}

class _SearchPanel extends StatelessWidget {
  const _SearchPanel({required this.controller, required this.onChanged});

  final TextEditingController controller;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    return TextField(
      key: const Key('markets-search'),
      controller: controller,
      onChanged: onChanged,
      decoration: InputDecoration(
        labelText: 'Search instruments',
        hintText: 'Symbol, description, broker path, or group',
        prefixIcon: const Icon(Icons.search),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  const _SectionLabel({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
        const SizedBox(height: 3),
        Text(
          subtitle,
          style: const TextStyle(fontSize: 12, color: Colors.white54),
        ),
      ],
    );
  }
}

class _InstrumentList extends StatelessWidget {
  const _InstrumentList({required this.instruments});

  final List<Mt5Instrument> instruments;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: instruments.length,
      separatorBuilder: (_, _) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        return _InstrumentCard(instrument: instruments[index]);
      },
    );
  }
}

class _InstrumentCard extends StatelessWidget {
  const _InstrumentCard({required this.instrument});

  final Mt5Instrument instrument;

  @override
  Widget build(BuildContext context) {
    return Container(
      key: ValueKey('instrument-${instrument.brokerSymbol}'),
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF121C2D),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      instrument.brokerSymbol,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      instrument.description,
                      style: const TextStyle(color: Colors.white70),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              _AvailabilityBadge(instrument: instrument),
            ],
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 24,
            runSpacing: 10,
            children: [
              _InstrumentDetail(label: 'Group', value: instrument.brokerGroup),
              _InstrumentDetail(label: 'Path', value: instrument.brokerPath),
              _InstrumentDetail(label: 'Base', value: instrument.currencyBase),
              _InstrumentDetail(
                label: 'Profit',
                value: instrument.currencyProfit,
              ),
              _InstrumentDetail(label: 'Digits', value: '${instrument.digits}'),
              _InstrumentDetail(
                label: 'Volume',
                value:
                    '${instrument.volumeMin} '
                    '– ${instrument.volumeMax}',
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _AvailabilityBadge extends StatelessWidget {
  const _AvailabilityBadge({required this.instrument});

  final Mt5Instrument instrument;

  @override
  Widget build(BuildContext context) {
    final available = instrument.canOpenNewOrders;

    final color = available
        ? Theme.of(context).colorScheme.primary
        : Theme.of(context).colorScheme.error;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(
        instrument.availabilityLabel,
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }
}

class _InstrumentDetail extends StatelessWidget {
  const _InstrumentDetail({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: Colors.white54),
          ),
          const SizedBox(height: 3),
          Text(
            value,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

class _MarketsStatePanel extends StatelessWidget {
  const _MarketsStatePanel({
    required this.icon,
    required this.title,
    required this.message,
    this.showProgress = false,
    this.action,
  });

  final IconData icon;
  final String title;
  final String message;
  final bool showProgress;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      constraints: const BoxConstraints(minHeight: 190),
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: const Color(0xFF121C2D),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 38, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 16),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.white60, height: 1.45),
          ),
          if (showProgress) ...[
            const SizedBox(height: 22),
            const SizedBox(width: 220, child: LinearProgressIndicator()),
          ],
          if (action != null) ...[const SizedBox(height: 20), action!],
        ],
      ),
    );
  }
}

String _availabilityFilterLabel(InstrumentAvailabilityFilter filter) {
  return switch (filter) {
    InstrumentAvailabilityFilter.all => 'All',
    InstrumentAvailabilityFilter.newOrdersAvailable => 'Available',
    InstrumentAvailabilityFilter.newOrdersBlocked => 'Blocked',
    InstrumentAvailabilityFilter.referenceOnly => 'Reference only',
    InstrumentAvailabilityFilter.closeOnly => 'Close only',
  };
}
