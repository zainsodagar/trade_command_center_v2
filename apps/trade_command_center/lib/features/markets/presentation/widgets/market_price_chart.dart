import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../../core/models/mt5_candle.dart';

class MarketPriceChart extends StatelessWidget {
  const MarketPriceChart({
    required this.candles,
    required this.digits,
    this.height = 280,
    super.key,
  });

  final List<Mt5Candle> candles;
  final int digits;
  final double height;

  @override
  Widget build(BuildContext context) {
    if (candles.isEmpty) {
      return Container(
        key: const Key('market-price-chart-empty'),
        width: double.infinity,
        height: height,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: Colors.white.withValues(alpha: 0.02),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white10),
        ),
        child: const Text(
          'No historical candles available for this timeframe.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.white54),
        ),
      );
    }

    final colorScheme = Theme.of(context).colorScheme;

    return Semantics(
      label: 'Historical candlestick chart',
      child: SizedBox(
        key: const Key('market-price-chart'),
        width: double.infinity,
        height: height,
        child: CustomPaint(
          painter: _CandlestickPainter(
            candles: candles,
            digits: digits,
            bullishColor: colorScheme.primary,
            bearishColor: colorScheme.error,
            gridColor: Colors.white.withValues(alpha: 0.08),
            labelColor: Colors.white54,
          ),
        ),
      ),
    );
  }
}

class _CandlestickPainter extends CustomPainter {
  const _CandlestickPainter({
    required this.candles,
    required this.digits,
    required this.bullishColor,
    required this.bearishColor,
    required this.gridColor,
    required this.labelColor,
  });

  final List<Mt5Candle> candles;
  final int digits;

  final Color bullishColor;
  final Color bearishColor;
  final Color gridColor;
  final Color labelColor;

  static const double _leftPadding = 12;
  static const double _rightPadding = 76;
  static const double _topPadding = 12;
  static const double _bottomPadding = 28;

  @override
  void paint(Canvas canvas, Size size) {
    if (candles.isEmpty) {
      return;
    }

    final chartWidth = size.width - _leftPadding - _rightPadding;

    final chartHeight = size.height - _topPadding - _bottomPadding;

    if (chartWidth <= 0 || chartHeight <= 0) {
      return;
    }

    var minimumPrice = candles.first.low;
    var maximumPrice = candles.first.high;

    for (final candle in candles.skip(1)) {
      minimumPrice = math.min(minimumPrice, candle.low);

      maximumPrice = math.max(maximumPrice, candle.high);
    }

    var priceRange = maximumPrice - minimumPrice;

    if (priceRange <= 0) {
      final fallbackPadding = math.max(
        maximumPrice.abs() * 0.001,
        math.pow(10, -digits).toDouble(),
      );

      minimumPrice -= fallbackPadding;
      maximumPrice += fallbackPadding;
      priceRange = maximumPrice - minimumPrice;
    }

    final pricePadding = priceRange * 0.05;

    minimumPrice -= pricePadding;
    maximumPrice += pricePadding;

    final paddedRange = maximumPrice - minimumPrice;

    final chartRect = Rect.fromLTWH(
      _leftPadding,
      _topPadding,
      chartWidth,
      chartHeight,
    );

    double priceToY(double price) {
      final normalized = (price - minimumPrice) / paddedRange;

      return chartRect.bottom - (normalized * chartRect.height);
    }

    _drawGrid(
      canvas: canvas,
      chartRect: chartRect,
      minimumPrice: minimumPrice,
      maximumPrice: maximumPrice,
      priceToY: priceToY,
    );

    _drawCandles(canvas: canvas, chartRect: chartRect, priceToY: priceToY);

    _drawTimeLabels(canvas: canvas, chartRect: chartRect);
  }

  void _drawGrid({
    required Canvas canvas,
    required Rect chartRect,
    required double minimumPrice,
    required double maximumPrice,
    required double Function(double) priceToY,
  }) {
    final paint = Paint()
      ..color = gridColor
      ..strokeWidth = 1;

    const gridLineCount = 5;

    for (var index = 0; index < gridLineCount; index += 1) {
      final fraction = index / (gridLineCount - 1);

      final price = maximumPrice - ((maximumPrice - minimumPrice) * fraction);

      final y = priceToY(price);

      canvas.drawLine(
        Offset(chartRect.left, y),
        Offset(chartRect.right, y),
        paint,
      );

      _paintText(
        canvas: canvas,
        text: price.toStringAsFixed(digits),
        offset: Offset(chartRect.right + 8, y - 7),
        fontSize: 10,
      );
    }
  }

  void _drawCandles({
    required Canvas canvas,
    required Rect chartRect,
    required double Function(double) priceToY,
  }) {
    final slotWidth = chartRect.width / candles.length;

    final bodyWidth = math.min(8.0, math.max(1.0, slotWidth * 0.58));

    for (var index = 0; index < candles.length; index += 1) {
      final candle = candles[index];

      final x = chartRect.left + (slotWidth * index) + (slotWidth / 2);

      final rising = candle.close >= candle.open;

      final candleColor = rising ? bullishColor : bearishColor;

      final wickPaint = Paint()
        ..color = candleColor
        ..strokeWidth = 1;

      canvas.drawLine(
        Offset(x, priceToY(candle.high)),
        Offset(x, priceToY(candle.low)),
        wickPaint,
      );

      final openY = priceToY(candle.open);

      final closeY = priceToY(candle.close);

      final bodyTop = math.min(openY, closeY);

      final bodyBottom = math.max(openY, closeY);

      final bodyHeight = math.max(1.0, bodyBottom - bodyTop);

      final bodyRect = Rect.fromLTWH(
        x - (bodyWidth / 2),
        bodyTop,
        bodyWidth,
        bodyHeight,
      );

      final bodyPaint = Paint()..color = candleColor;

      canvas.drawRect(bodyRect, bodyPaint);
    }
  }

  void _drawTimeLabels({required Canvas canvas, required Rect chartRect}) {
    if (candles.isEmpty) {
      return;
    }

    final first = _formatTime(candles.first.barTime);

    final last = _formatTime(candles.last.barTime);

    _paintText(
      canvas: canvas,
      text: first,
      offset: Offset(chartRect.left, chartRect.bottom + 8),
      fontSize: 10,
    );

    final lastPainter = _createTextPainter(text: last, fontSize: 10);

    lastPainter.paint(
      canvas,
      Offset(chartRect.right - lastPainter.width, chartRect.bottom + 8),
    );
  }

  String _formatTime(DateTime value) {
    final utc = value.toUtc();

    final hour = utc.hour.toString().padLeft(2, '0');

    final minute = utc.minute.toString().padLeft(2, '0');

    return '$hour:$minute UTC';
  }

  void _paintText({
    required Canvas canvas,
    required String text,
    required Offset offset,
    required double fontSize,
  }) {
    final painter = _createTextPainter(text: text, fontSize: fontSize);

    painter.paint(canvas, offset);
  }

  TextPainter _createTextPainter({
    required String text,
    required double fontSize,
  }) {
    return TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(color: labelColor, fontSize: fontSize),
      ),
      textDirection: TextDirection.ltr,
      maxLines: 1,
    )..layout();
  }

  @override
  bool shouldRepaint(covariant _CandlestickPainter oldDelegate) {
    return oldDelegate.candles != candles ||
        oldDelegate.digits != digits ||
        oldDelegate.bullishColor != bullishColor ||
        oldDelegate.bearishColor != bearishColor ||
        oldDelegate.gridColor != gridColor ||
        oldDelegate.labelColor != labelColor;
  }
}
