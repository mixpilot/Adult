from django.core.management.base import BaseCommand

from payments.services.reconcile import reconcile_pending_transactions


class Command(BaseCommand):
    help = 'Query Daraja for pending M-Pesa STK transactions that may have missed the callback.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-age',
            type=int,
            default=90,
            help='Only reconcile transactions pending longer than this many seconds (default: 90).',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum transactions to check per run (default: 20).',
        )

    def handle(self, *args, **options):
        summary = reconcile_pending_transactions(
            min_age_seconds=options['min_age'],
            limit=options['limit'],
        )
        self.stdout.write(self.style.SUCCESS(f"Reconcile complete: {summary}"))
