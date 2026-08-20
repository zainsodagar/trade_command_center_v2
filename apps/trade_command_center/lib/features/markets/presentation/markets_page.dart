import 'package:flutter/material.dart';

import '../../../core/models/mt5_candle_series.dart';
import '../../../core/models/mt5_instrument.dart';
import '../../../core/models/mt5_quote.dart';
import '../../../core/widgets/metric_card.dart';
import '../../../core/widgets/page_frame.dart';
import '../data/instrument_catalog_service.dart';
import '../data/market_data_service.dart';
import '../domain/instrument_catalog.dart';
import '../domain/instrument_catalog_loader.dart';
import '../domain/market_data_loader.dart';
import 'widgets/market_price_chart.dart';

class MarketsPage extends StatefulWidget {
  const MarketsPage({this.catalogLoader, this.marketDataLoader, super.key});

  final InstrumentCatalogLoader? catalogLoader;
  final MarketDataLoader? marketDataLoader;

  @override
  State<MarketsPage> createState() => _MarketsPageState();
}

class _MarketsPageState extends State<MarketsPage> {
  late final InstrumentCatalogLoader _catalogLoader;
  late final bool _ownsCatalogLoader;

  late final MarketDataLoader _marketDataLoader;
  late final bool _ownsMarketDataLoader;

  late final TextEditingController _searchController;

  InstrumentCatalog? _catalog;
  Object? _error;

  bool _loading = true;

  String _query = '';
  String? _selectedGroup;

  InstrumentAvailabilityFilter _availability = InstrumentAvailabilityFilter.all;

  static const String _defaultTimeframe = 'M1';

  static const List<String> _supportedTimeframes = [
    _defaultTimeframe,
    'M5',
    'M15',
    'M30',
    'H1',
    'H4',
    'D1',
  ];

  String? _selectedBrokerSymbol;
  String _selectedTimeframe = _defaultTimeframe;

  Mt5Quote? _selectedQuote;
  Mt5CandleSeries? _selectedCandles;

  bool _marketDataLoading = false;
  Object? _marketDataError;

  int _marketDataRequestId = 0;

  @override
  void initState() {
    super.initState();

    _searchController = TextEditingController();

    _ownsCatalogLoader = widget.catalogLoader == null;

    _catalogLoader = widget.catalogLoader ?? InstrumentCatalogService();

    _ownsMarketDataLoader = widget.marketDataLoader == null;

    _marketDataLoader = widget.marketDataLoader ?? MarketDataService();

    _loadCatalog();
  }

  @override
  void dispose() {
    _searchController.dispose();

    if (_ownsCatalogLoader) {
      _catalogLoader.close();
    }

    if (_ownsMarketDataLoader) {
      _marketDataLoader.close();
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

  Future<void> _selectInstrument(Mt5Instrument instrument) async {
    final requestId = ++_marketDataRequestId;

    setState(() {
      _selectedBrokerSymbol = instrument.brokerSymbol;
      _selectedTimeframe = _defaultTimeframe;

      _selectedQuote = null;
      _selectedCandles = null;

      _marketDataLoading = true;
      _marketDataError = null;
    });

    final quoteFuture = _marketDataLoader.loadQuote(instrument.brokerSymbol);

    final candlesFuture = _marketDataLoader.loadCandles(
      brokerSymbol: instrument.brokerSymbol,
      timeframe: _selectedTimeframe,
      count: 100,
    );

    try {
      final results = await Future.wait<Object?>([quoteFuture, candlesFuture]);

      final quote = results[0] as Mt5Quote;
      final candles = results[1] as Mt5CandleSeries;

      if (!mounted || requestId != _marketDataRequestId) {
        return;
      }

      setState(() {
        _selectedQuote = quote;
        _selectedCandles = candles;

        _marketDataLoading = false;
        _marketDataError = null;
      });
    } catch (error) {
      if (!mounted || requestId != _marketDataRequestId) {
        return;
      }

      setState(() {
        _selectedQuote = null;
        _selectedCandles = null;

        _marketDataLoading = false;
        _marketDataError = error;
      });
    }
  }

  Future<void> _selectTimeframe(String timeframe) async {
    if (!_supportedTimeframes.contains(timeframe)) {
      return;
    }

    if (timeframe == _selectedTimeframe) {
      return;
    }

    final brokerSymbol = _selectedBrokerSymbol;

    if (brokerSymbol == null) {
      return;
    }

    final requestId = ++_marketDataRequestId;

    setState(() {
      _selectedTimeframe = timeframe;
      _selectedCandles = null;

      _marketDataLoading = true;
      _marketDataError = null;
    });

    try {
      final candles = await _marketDataLoader.loadCandles(
        brokerSymbol: brokerSymbol,
        timeframe: timeframe,
        count: 100,
      );

      if (!mounted || requestId != _marketDataRequestId) {
        return;
      }

      setState(() {
        _selectedCandles = candles;

        _marketDataLoading = false;
        _marketDataError = null;
      });
    } catch (error) {
      if (!mounted || requestId != _marketDataRequestId) {
        return;
      }

      setState(() {
        _selectedCandles = null;

        _marketDataLoading = false;
        _marketDataError = error;
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
          if (_selectedBrokerSymbol != null) ...[
            _MarketDataSelectionPanel(
              brokerSymbol: _selectedBrokerSymbol!,
              quote: _selectedQuote,
              candles: _selectedCandles,
              timeframe: _selectedTimeframe,
              supportedTimeframes: _supportedTimeframes,
              onTimeframeSelected: _selectTimeframe,
              loading: _marketDataLoading,
              error: _marketDataError,
            ),
            const SizedBox(height: 16),
          ],
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
          _InstrumentList(
            instruments: filtered,
            selectedBrokerSymbol: _selectedBrokerSymbol,
            onSelected: _selectInstrument,
          ),
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
  const _InstrumentList({
    required this.instruments,
    required this.selectedBrokerSymbol,
    required this.onSelected,
  });

  final List<Mt5Instrument> instruments;
  final String? selectedBrokerSymbol;
  final ValueChanged<Mt5Instrument> onSelected;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: instruments.length,
      separatorBuilder: (_, _) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final instrument = instruments[index];

        return _InstrumentCard(
          instrument: instrument,
          selected: selectedBrokerSymbol == instrument.brokerSymbol,
          onTap: () => onSelected(instrument),
        );
      },
    );
  }
}

class _InstrumentCard extends StatelessWidget {
  const _InstrumentCard({
    required this.instrument,
    required this.selected,
    required this.onTap,
  });

  final Mt5Instrument instrument;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final selectedColor = Theme.of(context).colorScheme.primary;

    return Container(
      key: ValueKey('instrument-${instrument.brokerSymbol}'),
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFF121C2D),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: selected
              ? selectedColor.withValues(alpha: 0.75)
              : Colors.white10,
          width: selected ? 1.5 : 1,
        ),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
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
                  _InstrumentDetail(
                    label: 'Group',
                    value: instrument.brokerGroup,
                  ),
                  _InstrumentDetail(
                    label: 'Path',
                    value: instrument.brokerPath,
                  ),
                  _InstrumentDetail(
                    label: 'Base',
                    value: instrument.currencyBase,
                  ),
                  _InstrumentDetail(
                    label: 'Profit',
                    value: instrument.currencyProfit,
                  ),
                  _InstrumentDetail(
                    label: 'Digits',
                    value: '${instrument.digits}',
                  ),
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
        ),
      ),
    );
  }
}

class _MarketDataSelectionPanel extends StatelessWidget {
  const _MarketDataSelectionPanel({
    required this.brokerSymbol,
    required this.quote,
    required this.candles,
    required this.timeframe,
    required this.supportedTimeframes,
    required this.onTimeframeSelected,
    required this.loading,
    required this.error,
  });

  final String brokerSymbol;
  final Mt5Quote? quote;
  final Mt5CandleSeries? candles;

  final String timeframe;
  final List<String> supportedTimeframes;
  final ValueChanged<String> onTimeframeSelected;

  final bool loading;
  final Object? error;

  @override
  Widget build(BuildContext context) {
    final icon = error != null
        ? Icons.warning_amber_outlined
        : loading
        ? Icons.sync
        : Icons.query_stats_outlined;

    final message = error != null
        ? 'Unable to load read-only $timeframe market data.\n\n$error'
        : loading
        ? 'Loading live quote and $timeframe historical candles '
              'through the local execution agent.'
        : 'Read-only live quote and $timeframe historical candles loaded.';

    return Container(
      key: const Key('markets-selected-market-data'),
      width: double.infinity,
      padding: const EdgeInsets.all(18),
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
              Icon(icon, color: Theme.of(context).colorScheme.primary),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '$brokerSymbol market data',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      message,
                      style: const TextStyle(
                        color: Colors.white60,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 18),
          const Text(
            'Timeframe',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final option in supportedTimeframes)
                ChoiceChip(
                  key: ValueKey('markets-timeframe-$option'),
                  label: Text(option),
                  selected: timeframe == option,
                  onSelected: loading
                      ? null
                      : (_) => onTimeframeSelected(option),
                ),
            ],
          ),
          if (loading) ...[
            const SizedBox(height: 14),
            const LinearProgressIndicator(),
          ],
          if (!loading && error == null) ...[
            const SizedBox(height: 18),
            _buildMarketDataValues(),
            if (candles != null) ...[
              const SizedBox(height: 22),
              const Text(
                'Historical Price',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: Colors.white70,
                ),
              ),
              const SizedBox(height: 10),
              MarketPriceChart(
                candles: candles!.candles,
                digits: candles!.digits,
              ),
            ],
          ],
        ],
      ),
    );
  }

  Widget _buildMarketDataValues() {
    final currentQuote = quote;
    final currentCandles = candles;

    if (currentQuote == null || currentCandles == null) {
      return const Text(
        'Market data is not currently available.',
        style: TextStyle(color: Colors.white60),
      );
    }

    return Wrap(
      spacing: 24,
      runSpacing: 16,
      children: [
        _MarketDataValue(
          label: 'Bid',
          value: _formatPrice(currentQuote.bid, currentQuote.digits),
        ),
        _MarketDataValue(
          label: 'Ask',
          value: _formatPrice(currentQuote.ask, currentQuote.digits),
        ),
        _MarketDataValue(
          label: 'Spread',
          value: _formatPrice(currentQuote.spread, currentQuote.digits),
        ),
        _MarketDataValue(
          label: 'Spread Points',
          value: _formatNumber(currentQuote.spreadPoints),
        ),
        _MarketDataValue(
          label: 'Tick Time',
          value: _formatDateTime(currentQuote.tickTime),
        ),
        _MarketDataValue(
          label: 'Quote Status',
          value: currentQuote.quoteAvailable
              ? 'Available'
              : _formatUnavailableReason(currentQuote.unavailableReason),
        ),
        _MarketDataValue(label: 'Timeframe', value: currentCandles.timeframe),
        _MarketDataValue(
          label: 'Candle Count',
          value: '${currentCandles.candleCount}',
        ),
        _MarketDataValue(
          label: 'Oldest Candle',
          value: _formatDateTime(currentCandles.oldestCandleTime),
        ),
        _MarketDataValue(
          label: 'Latest Candle',
          value: _formatDateTime(currentCandles.latestCandleTime),
        ),
        _MarketDataValue(
          label: 'History Status',
          value: currentCandles.candlesAvailable
              ? 'Available'
              : _formatUnavailableReason(currentCandles.unavailableReason),
        ),
      ],
    );
  }
}

class _MarketDataValue extends StatelessWidget {
  const _MarketDataValue({required this.label, required this.value});

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
          const SizedBox(height: 4),
          Text(
            value,
            key: ValueKey('market-data-$label'),
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}

String _formatPrice(double? value, int digits) {
  if (value == null) {
    return 'Unavailable';
  }

  return value.toStringAsFixed(digits);
}

String _formatNumber(double? value) {
  if (value == null) {
    return 'Unavailable';
  }

  return value.toStringAsFixed(2);
}

String _formatDateTime(DateTime? value) {
  if (value == null) {
    return 'Unavailable';
  }

  return value.toUtc().toIso8601String();
}

String _formatUnavailableReason(String? value) {
  if (value == null || value.trim().isEmpty) {
    return 'Unavailable';
  }

  return value;
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
