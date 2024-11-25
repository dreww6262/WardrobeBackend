import os

import structlog
from django.contrib.auth import get_user_model
from django.core import management
from django.core.management.base import BaseCommand
from django.test.runner import DiscoverRunner

logger = structlog.getLogger(__name__)


class Command(BaseCommand):
    help = "Start Server"

    def handle(self, *args, **options):
        if os.environ.get("AUTO_MAKEMIGRATIONS") == "Y":
            management.call_command("makemigrations")
        if os.environ.get("AUTO_MIGRATE") != "N":
            management.call_command("migrate")

        if os.environ.get("AUTO_TEST") == "Y":
            logger.info("Running Tests")
            num_parallel_processes = int(
                os.environ.get("DJANGO_TEST_PROCESSES", "1")
            )
            runner = DiscoverRunner(parallel=num_parallel_processes)
            failures = runner.run_tests(None)
            if failures:
                logger.error("Tests Failed", failures=failures)
            else:
                logger.info("All tests passed")

        auth_params = {
            "username": os.environ.get("LOCAL_DEV_USERNAME", "a@a.com"),
            "password": os.environ.get("LOCAL_DEV_PASSWORD", "a"),
        }
        params = {
            "email": auth_params["username"],
            "is_staff": True,
            "is_superuser": True,
        }
        try:
            user = get_user_model().objects.get(email=params["email"])
        except Exception:
            user = get_user_model().objects.create(**params)

        user.set_password(auth_params["password"])
        user.save()

        logger.info("########################################")
        logger.info("You can log in with:")
        logger.info(f"Username: {auth_params['username']}")
        logger.info(f"Password: {auth_params['password']}")
        logger.info("########################################")
        logger.info(
            "Set LOCAL_DEV_USERNAME and LOCAL_DEV_PASSWORD in your"
            " .env file to change these values"
        )
        logger.info("########################################")
        logger.info(
            "Set AUTO_MIGRATE (default is Y) to False"
            " to prevent automatically running migrations"
        )
        logger.info(
            "Set AUTO_MAKEMIGRATIONS to Y (default is False) to "
            "automatically make new migrations on server restart"
        )
        logger.info("########################################")

        management.call_command("runserver", "0:8000")
