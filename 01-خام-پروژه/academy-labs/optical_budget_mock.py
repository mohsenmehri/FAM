"""Illustrative optical loss budget arithmetic; no transceiver or light measured."""


import math


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite numeric values required")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError("numeric value out of range") from exc
    if not math.isfinite(value):
        raise ValueError("finite numeric values required")
    return value


def calculate(tx_dbm, receiver_min_dbm, components_db, margin_db):
    """Simplified worst-case budget; no connector aging or dispersion model."""
    if not isinstance(components_db, (list, tuple)):
        raise ValueError("components must be a list or tuple")
    values = [_number(v) for v in components_db]
    tx_dbm, receiver_min_dbm, margin_db = map(_number, (tx_dbm, receiver_min_dbm, margin_db))
    if not values or any(v < 0 for v in values) or margin_db < 0:
        raise ValueError('nonnegative losses, nonempty components and margin required')
    try:
        total_loss = math.fsum(values)
        predicted_rx = tx_dbm - total_loss
        available_margin = predicted_rx - receiver_min_dbm
    except OverflowError as exc:
        raise ValueError("budget calculation overflow") from exc
    if not all(map(math.isfinite, (total_loss, predicted_rx, available_margin))):
        raise ValueError("budget calculation overflow")
    return {'total_loss_db': total_loss, 'predicted_rx_dbm': predicted_rx,
            'available_margin_db': available_margin, 'meets_margin': available_margin >= margin_db}


if __name__ == '__main__':
    print('Illustrative only:', calculate(-3, -15, [4, 1, 1], 3))
    print('No optics or network accessed')
