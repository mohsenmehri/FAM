"""Illustrative optical loss budget arithmetic; no transceiver or light measured."""


def calculate(tx_dbm, receiver_min_dbm, components_db, margin_db):
    """Simplified worst-case budget; no connector aging or dispersion model."""
    values = list(components_db)
    if not values or any(v < 0 for v in values) or margin_db < 0:
        raise ValueError('nonnegative losses, nonempty components and margin required')
    total_loss = sum(values)
    predicted_rx = tx_dbm - total_loss
    available_margin = predicted_rx - receiver_min_dbm
    return {'total_loss_db': total_loss, 'predicted_rx_dbm': predicted_rx,
            'available_margin_db': available_margin, 'meets_margin': available_margin >= margin_db}


if __name__ == '__main__':
    print('Illustrative only:', calculate(-3, -15, [4, 1, 1], 3))
    print('No optics or network accessed')
