# Payments app – M-Pesa STK Push (prompt) only

This app handles **only** M-Pesa prompts (Safaricom Daraja API – Lipa Na M-Pesa Online / STK Push). Other payment methods (Airtel Money, manual M-Pesa Pay Bill, etc.) remain in the **subscriptions** app.

## Flow

1. User selects a plan and chooses **M-Pesa** as payment method, enters phone number.
2. **Subscriptions** app creates a `Payment` (pending) and calls this app’s service to initiate STK Push.
3. **Payments** app calls Daraja API (OAuth + STK Push). User receives prompt on their phone.
4. User enters M-Pesa PIN on phone. Safaricom sends result to our **callback URL**.
5. **Payments** callback view receives the result, updates `MpesaTransaction`, and activates the subscription (completes `Payment`, creates/updates `Subscription`).
6. The waiting page **polls local DB only** (`/payments/mpesa/status/<id>/`) — no Daraja query on each poll.
7. **Background reconcile** (`python manage.py reconcile_mpesa`) queries Daraja for pending transactions that missed the callback (run via cron every 2–5 minutes).

## Configuration

In `config/settings.py` (or environment variables):

| Setting | Description |
|--------|-------------|
| `MPESA_ENV` | `sandbox` or `production` |
| `MPESA_CONSUMER_KEY` | Daraja app consumer key |
| `MPESA_CONSUMER_SECRET` | Daraja app consumer secret |
| `MPESA_SHORTCODE` | Paybill or Till number |
| `MPESA_SHORTCODE_TYPE` | `till` (Buy Goods / `CustomerBuyGoodsOnline`) or `paybill` (`CustomerPayBillOnline`). Default: `till`. |
| `MPESA_PASSKEY` | Lipa Na M-Pesa passkey from Daraja |
| `MPESA_CALLBACK_BASE_URL` | Base URL for callbacks (must be HTTPS in production). Callback path: `{MPESA_CALLBACK_BASE_URL}/payments/mpesa/callback/` |

For **local testing**, use a tunnel (e.g. ngrok) and set `MPESA_CALLBACK_BASE_URL` to your public URL (e.g. `https://abc123.ngrok.io`).

## URLs

- `GET /payments/mpesa/callback/` – Health check (returns JSON `status: ok`). Use to verify the URL is public.
- `POST /payments/mpesa/callback/` – Daraja callback (CSRF exempt). Do not require auth.
- `GET /payments/mpesa/status/<payment_id>/` – Local status poll (auth required). Reads DB only; updated by callback.

## Background reconcile (missed callbacks)

```bash
python manage.py reconcile_mpesa
# Optional: only txns pending 2+ minutes, max 10 per run
python manage.py reconcile_mpesa --min-age 120 --limit 10
```

**Cron example** (every 3 minutes):

```cron
*/3 * * * * cd /path/to/Adult && ./venv/bin/python manage.py reconcile_mpesa >> /var/log/mpesa_reconcile.log 2>&1
```

## Models

- **MpesaTransaction** – One record per STK Push: `account_reference` (e.g. `sub_<payment_id>`), phone, amount, `checkout_request_id`, status, `mpesa_receipt_number`, callback metadata.

## Extending (e.g. tokens, tips)

To use M-Pesa prompt for token purchase or tips:

1. Create a `Payment` (or equivalent) in your app.
2. Call `MpesaService().initiate_stk_push(phone, amount, account_reference, transaction_desc)` with a unique `account_reference` (e.g. `tokens_<order_id>`).
3. Create an `MpesaTransaction` with the returned `checkout_request_id` and `merchant_request_id`.
4. In `payments/views.py`, extend `_handle_successful_payment(txn)` to handle your `account_reference` prefix (e.g. `tokens_`) and credit tokens or complete the order.
