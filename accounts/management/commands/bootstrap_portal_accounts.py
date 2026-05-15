from __future__ import annotations

import secrets

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import User


class Command(BaseCommand):
    help = "Create grade portal accounts (1–11) and optionally teacher accounts from Staff."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            help="Set the same password for created accounts (otherwise random passwords are generated).",
        )
        parser.add_argument(
            "--reset-passwords",
            action="store_true",
            help="Also reset passwords for existing accounts that match the criteria.",
        )
        parser.add_argument(
            "--teachers-from-staff",
            action="store_true",
            help="Create one teacher user per Staff(role='teacher') without a linked user.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be created/changed without writing to the database.",
        )

    def handle(self, *args, **options):
        password = options.get("password")
        reset_passwords = bool(options.get("reset_passwords"))
        teachers_from_staff = bool(options.get("teachers_from_staff"))
        dry_run = bool(options.get("dry_run"))

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: no database changes will be made."))

        with transaction.atomic():
            self._bootstrap_grade_accounts(password=password, reset_passwords=reset_passwords, dry_run=dry_run)
            if teachers_from_staff:
                self._bootstrap_teacher_accounts(password=password, reset_passwords=reset_passwords, dry_run=dry_run)

            if dry_run:
                transaction.set_rollback(True)

    def _password_for(self, password: str | None) -> str:
        return password or secrets.token_urlsafe(10)

    def _bootstrap_grade_accounts(self, *, password: str | None, reset_passwords: bool, dry_run: bool) -> None:
        from django.db.utils import OperationalError, ProgrammingError

        self.stdout.write("Grade accounts:")
        for grade in range(1, 12):
            try:
                user, created = User.objects.get_or_create(
                    role=User.Role.STUDENT,
                    grade=grade,
                    defaults={"username": f"grade{grade}"},
                )
            except (OperationalError, ProgrammingError) as exc:
                raise CommandError("Database is not migrated yet. Run `python manage.py migrate` first.") from exc

            if created or reset_passwords:
                new_password = self._password_for(password)
                user.set_password(new_password)
                if not dry_run:
                    user.save(update_fields=["password"])
                self.stdout.write(f"- grade {grade}: {user.username} (password: {new_password})")
            else:
                self.stdout.write(f"- grade {grade}: {user.username} (exists)")

    def _bootstrap_teacher_accounts(self, *, password: str | None, reset_passwords: bool, dry_run: bool) -> None:
        from django.db.utils import OperationalError, ProgrammingError
        from people.models import Staff

        try:
            staff_members = list(Staff.objects.filter(role="teacher").select_related("user").order_by("id"))
        except (OperationalError, ProgrammingError) as exc:
            raise CommandError("Database is not migrated yet. Run `python manage.py migrate` first.") from exc
        self.stdout.write("Teacher accounts (from Staff):")

        for staff in staff_members:
            if staff.user_id:
                if reset_passwords:
                    new_password = self._password_for(password)
                    staff.user.set_password(new_password)
                    if not dry_run:
                        staff.user.save(update_fields=["password"])
                    self.stdout.write(f"- {staff.full_name}: {staff.user.username} (password: {new_password})")
                else:
                    self.stdout.write(f"- {staff.full_name}: {staff.user.username} (exists)")
                continue

            username = f"teacher{staff.pk}"
            user = User(username=username, role=User.Role.TEACHER)
            new_password = self._password_for(password)
            user.set_password(new_password)

            if not dry_run:
                user.save()
                staff.user = user
                staff.save(update_fields=["user"])

            self.stdout.write(f"- {staff.full_name}: {username} (password: {new_password})")
