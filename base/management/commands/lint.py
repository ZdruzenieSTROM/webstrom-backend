from typing import Any, Optional

from django.conf import settings
from django.core.management import BaseCommand, call_command

from pylint.lint import Run as run_pylint


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        run_pylint(settings.LOCAL_APPS)
