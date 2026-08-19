import 'instrument_catalog.dart';

abstract interface class InstrumentCatalogLoader {
  Future<InstrumentCatalog> load();

  void close();
}
