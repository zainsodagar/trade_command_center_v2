import 'dart:io';

import 'package:trade_command_center/core/services/agent_api.dart';
import 'package:trade_command_center/core/services/backend_api.dart';

Future<void> main() async {
  final backendApi = BackendApi();
  final agentApi = AgentApi();

  try {
    final backend = await backendApi.getSystemStatus();
    final agent = await agentApi.getAgentStatus();
    final mt5 = await agentApi.getMt5Status();

    stdout.writeln('Backend:');
    stdout.writeln('  online = ${backend.isOnline}');
    stdout.writeln('  brokerConnections = ${backend.brokerConnections}');
    stdout.writeln('  executionEnabled = ${backend.executionEnabled}');
    stdout.writeln('  liveTradingEnabled = ${backend.liveTradingEnabled}');
    stdout.writeln('  readOnlySafe = ${backend.isReadOnlySafe}');

    stdout.writeln();

    stdout.writeln('Agent:');
    stdout.writeln('  online = ${agent.isOnline}');
    stdout.writeln('  mt5Enabled = ${agent.mt5Enabled}');
    stdout.writeln('  mt5Connected = ${agent.mt5Connected}');
    stdout.writeln('  executionEnabled = ${agent.executionEnabled}');
    stdout.writeln('  liveTradingEnabled = ${agent.liveTradingEnabled}');
    stdout.writeln('  readOnlySafe = ${agent.isReadOnlySafe}');

    stdout.writeln();

    stdout.writeln('MT5:');
    stdout.writeln('  enabled = ${mt5.enabled}');
    stdout.writeln('  terminalAvailable = ${mt5.terminalAvailable}');
    stdout.writeln('  connected = ${mt5.connected}');
    stdout.writeln('  accountLoggedIn = ${mt5.accountLoggedIn}');
    stdout.writeln('  accountLoginMasked = ${mt5.accountLoginMasked}');
    stdout.writeln('  accountMode = ${mt5.accountMode}');
    stdout.writeln('  accountServer = ${mt5.accountServer}');
    stdout.writeln('  accountCurrency = ${mt5.accountCurrency}');
    stdout.writeln('  accountLeverage = ${mt5.accountLeverage}');
    stdout.writeln('  executionEnabled = ${mt5.executionEnabled}');
    stdout.writeln('  liveTradingEnabled = ${mt5.liveTradingEnabled}');
    stdout.writeln('  readOnlySafe = ${mt5.isReadOnlySafe}');
    stdout.writeln('  demoAccount = ${mt5.isDemoAccount}');
    stdout.writeln('  operationalReadOnly = ${mt5.isOperationalReadOnly}');
    stdout.writeln('  message = ${mt5.message}');

    if (!backend.isOnline) {
      throw StateError('Backend is not online.');
    }

    if (!backend.isReadOnlySafe) {
      throw StateError('Backend is not in read-only safe state.');
    }

    if (!agent.isOnline) {
      throw StateError('Execution agent is not online.');
    }

    if (!agent.mt5Enabled) {
      throw StateError('MT5 integration is not enabled.');
    }

    if (!agent.mt5Connected) {
      throw StateError('MT5 terminal is not connected.');
    }

    if (!agent.isReadOnlySafe) {
      throw StateError('Execution agent is not in read-only safe state.');
    }

    if (!mt5.isReadOnlySafe) {
      throw StateError('Detailed MT5 status is not read-only safe.');
    }

    if (!mt5.isDemoAccount) {
      throw StateError('MT5 account is not demo.');
    }

    if (!mt5.isOperationalReadOnly) {
      throw StateError('MT5 is not operational in read-only demo mode.');
    }

    if (mt5.accountLoginMasked == null || mt5.accountLoginMasked!.isEmpty) {
      throw StateError('Masked MT5 login is unavailable.');
    }

    stdout.writeln();
    stdout.writeln('DART DETAILED MT5 READ-ONLY STATUS CONFIRMED');
  } finally {
    backendApi.close();
    agentApi.close();
  }
}
