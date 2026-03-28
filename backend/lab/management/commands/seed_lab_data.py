from django.conf import settings
from django.core.management.base import BaseCommand

from lab.seeds import seed_extraction_methods


class Command(BaseCommand):
    help = "Seed lab configuration data such as extraction methods."

    def handle(self, *args, **options):
        methods = seed_extraction_methods(settings)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(methods)} extraction methods."))
        for method in methods:
            self.stdout.write(
                f"- {method.slug} | visible={method.is_visible} | enabled={method.is_enabled}"
            )
