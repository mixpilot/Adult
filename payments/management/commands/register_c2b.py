from django.core.management.base import BaseCommand

from payments.services.c2b import c2b_urls, register_c2b_urls


class Command(BaseCommand):
    help = 'Register C2B validation and confirmation URLs with Safaricom Daraja.'

    def handle(self, *args, **options):
        urls = c2b_urls()
        self.stdout.write(f"Validation URL:   {urls['validation']}")
        self.stdout.write(f"Confirmation URL: {urls['confirmation']}")
        result = register_c2b_urls()
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"Registered: {result.get('data')}"))
        else:
            self.stdout.write(self.style.ERROR(f"Failed: {result.get('error')}"))
