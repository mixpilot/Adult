"""User-facing M-Pesa error messages."""

# Safaricom STK ResultCode → helpful message
STK_RESULT_HINTS = {
    2002: (
        'Till setup error: your head office (agent) number and till (store) number do not match. '
        'Set MPESA_SHORTCODE to your head office shortcode from Safaricom and '
        'MPESA_TILL_NUMBER to your till (e.g. 4501829). The passkey must be for the head office shortcode.'
    ),
    2029: 'M-Pesa could not process this till payment. Confirm Lipa Na M-Pesa Online is enabled for your till on Daraja.',
    1032: 'Payment cancelled on your phone.',
    1037: 'Payment timed out. Check your phone for the M-Pesa prompt and try again.',
    1: 'Payment failed. Check your M-Pesa balance and try again.',
}


def humanize_stk_failure(result_code, result_desc: str = '') -> str:
    """Return a clear message for failed STK results."""
    try:
        code = int(result_code)
    except (TypeError, ValueError):
        code = None
    if code is not None and code in STK_RESULT_HINTS:
        return STK_RESULT_HINTS[code]
    if result_desc:
        return result_desc
    return 'Payment failed or was cancelled.'
