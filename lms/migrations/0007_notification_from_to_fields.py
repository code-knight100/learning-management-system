from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_notification_user_to_to(apps, schema_editor):
    Notification = apps.get_model("lms", "Notification")
    for notification in Notification.objects.exclude(user_id=None):
        notification.To_id = notification.user_id
        notification.save(update_fields=["To"])


class Migration(migrations.Migration):

    dependencies = [
        ("lms", "0006_alter_sponsorship_student"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="From",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_notifications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="To",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_notifications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(copy_notification_user_to_to, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="notification",
            name="user",
        ),
    ]
