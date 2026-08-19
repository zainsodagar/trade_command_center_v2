import '../../../core/services/agent_api.dart';
import '../../../core/services/backend_api.dart';
import '../domain/dashboard_status.dart';
import '../domain/dashboard_status_loader.dart';

class DashboardStatusService implements DashboardStatusLoader {
  DashboardStatusService({BackendApi? backendApi, AgentApi? agentApi})
    : _backendApi = backendApi ?? BackendApi(),
      _agentApi = agentApi ?? AgentApi(),
      _ownsBackendApi = backendApi == null,
      _ownsAgentApi = agentApi == null;

  final BackendApi _backendApi;
  final AgentApi _agentApi;

  final bool _ownsBackendApi;
  final bool _ownsAgentApi;

  @override
  Future<DashboardStatus> load() async {
    final backend = await _backendApi.getSystemStatus();

    final agent = await _agentApi.getAgentStatus();

    final mt5 = await _agentApi.getMt5Status();

    return DashboardStatus(backend: backend, agent: agent, mt5: mt5);
  }

  @override
  void close() {
    if (_ownsBackendApi) {
      _backendApi.close();
    }

    if (_ownsAgentApi) {
      _agentApi.close();
    }
  }
}
