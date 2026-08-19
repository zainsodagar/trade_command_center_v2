import '../../../core/models/mt5_instrument.dart';

enum InstrumentAvailabilityFilter {
  all,
  newOrdersAvailable,
  newOrdersBlocked,
  referenceOnly,
  closeOnly,
}

class InstrumentCatalog {
  InstrumentCatalog(List<Mt5Instrument> instruments)
    : instruments = List<Mt5Instrument>.unmodifiable(instruments);

  final List<Mt5Instrument> instruments;

  int get totalCount => instruments.length;

  int get newOrdersAvailableCount =>
      instruments.where((instrument) => instrument.canOpenNewOrders).length;

  int get newOrdersBlockedCount =>
      instruments.where((instrument) => !instrument.canOpenNewOrders).length;

  int get referenceOnlyCount =>
      instruments.where((instrument) => instrument.referenceOnly).length;

  int get closeOnlyCount =>
      instruments.where((instrument) => instrument.isCloseOnly).length;

  List<String> get brokerGroups {
    final groups = instruments
        .map((instrument) => instrument.brokerGroup.trim())
        .where((group) => group.isNotEmpty)
        .toSet()
        .toList();

    groups.sort(
      (left, right) => left.toLowerCase().compareTo(right.toLowerCase()),
    );

    return List<String>.unmodifiable(groups);
  }

  Map<String, int> get groupCounts {
    final counts = <String, int>{};

    for (final instrument in instruments) {
      counts.update(
        instrument.brokerGroup,
        (count) => count + 1,
        ifAbsent: () => 1,
      );
    }

    return Map<String, int>.unmodifiable(counts);
  }

  List<Mt5Instrument> filter({
    String query = '',
    String? brokerGroup,
    InstrumentAvailabilityFilter availability =
        InstrumentAvailabilityFilter.all,
  }) {
    final normalizedQuery = query.trim().toLowerCase();

    final normalizedGroup = brokerGroup?.trim().toLowerCase();

    final matches = instruments
        .where((instrument) {
          if (normalizedGroup != null &&
              normalizedGroup.isNotEmpty &&
              instrument.brokerGroup.toLowerCase() != normalizedGroup) {
            return false;
          }

          if (!_matchesAvailability(instrument, availability)) {
            return false;
          }

          if (normalizedQuery.isEmpty) {
            return true;
          }

          return instrument.brokerSymbol.toLowerCase().contains(
                normalizedQuery,
              ) ||
              instrument.description.toLowerCase().contains(normalizedQuery) ||
              instrument.brokerPath.toLowerCase().contains(normalizedQuery) ||
              instrument.brokerGroup.toLowerCase().contains(normalizedQuery);
        })
        .toList(growable: false);

    return List<Mt5Instrument>.unmodifiable(matches);
  }

  bool _matchesAvailability(
    Mt5Instrument instrument,
    InstrumentAvailabilityFilter filter,
  ) {
    return switch (filter) {
      InstrumentAvailabilityFilter.all => true,
      InstrumentAvailabilityFilter.newOrdersAvailable =>
        instrument.canOpenNewOrders,
      InstrumentAvailabilityFilter.newOrdersBlocked =>
        !instrument.canOpenNewOrders,
      InstrumentAvailabilityFilter.referenceOnly => instrument.referenceOnly,
      InstrumentAvailabilityFilter.closeOnly => instrument.isCloseOnly,
    };
  }
}
