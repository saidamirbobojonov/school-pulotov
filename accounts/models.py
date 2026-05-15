from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", _("Student")
        TEACHER = "teacher", _("Teacher")

    role = models.CharField(max_length=16, choices=Role.choices, default=Role.STUDENT)
    grade = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta(AbstractUser.Meta):
        constraints = [
            models.CheckConstraint(
                condition=models.Q(grade__isnull=True)
                | (models.Q(grade__gte=1) & models.Q(grade__lte=11)),
                name="user_grade_1_11_or_null",
            ),
            models.CheckConstraint(
                condition=models.Q(role="student") | models.Q(grade__isnull=True),
                name="user_teacher_grade_null",
            ),
            models.UniqueConstraint(
                fields=["grade"],
                condition=models.Q(role="student") & models.Q(grade__isnull=False),
                name="uniq_student_grade_account",
            ),
        ]

    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    def is_teacher(self) -> bool:
        return self.role == self.Role.TEACHER
