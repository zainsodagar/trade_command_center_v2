import '../../../core/services/agent_api.dart';
import '../domain/instrument_catalog.dart';
import '../domain/instrument_catalog_loader.dart';

class InstrumentCatalogService implements InstrumentCatalogLoader {
  InstrumentCatalogService({AgentApi? agentApi})
    : _agentApi = agentApi ?? AgentApi(),
      _ownsAgentApi = agentApi == null;

  final AgentApi _agentApi;
  final bool _ownsAgentApi;

  @override
  Future<InstrumentCatalog> load() async {
    final instruments = await _agentApi.getMt5Instruments();

    return InstrumentCatalog(instruments);
  }

  @override
  void close() {
    if (_ownsAgentApi) {
      _agentApi.close();
    }
  }
}
