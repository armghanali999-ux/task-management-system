from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("activity", "0002_initial")]

    operations = [
        migrations.AlterField(
            model_name="activitylog",
            name="activity_type",
            field=models.CharField(
                choices=[
                    ("created", "Created"),
                    ("updated", "Updated"),
                    ("deleted", "Deleted"),
                    ("status_changed", "Status Changed"),
                    ("assigned", "Assigned"),
                    ("commented", "Commented"),
                    ("member_added", "Member Added"),
                    ("member_removed", "Member Removed"),
                    ("project_created", "Project Created"),
                    ("task_created", "Task Created"),
                    ("task_updated", "Task Updated"),
                    ("user_created", "User Created"),
                    ("user_updated", "User Updated"),
                ],
                db_index=True,
                max_length=50,
            ),
        )
    ]
