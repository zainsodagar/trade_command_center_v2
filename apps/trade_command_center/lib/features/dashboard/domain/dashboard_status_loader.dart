import 'dashboard_status.dart';

abstract interface class DashboardStatusLoader {
  Future<DashboardStatus> load();

  void close();
}
