# Generated by Django 4.2.11 on 2024-05-27 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("providers", "0071_alter_tgesettings_my_toll_token"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="EShipperSettings",
            new_name="EShipperXMLSettings",
        ),
        migrations.AlterModelOptions(
            name="eshipperxmlsettings",
            options={
                "verbose_name": "eShipper XML Settings",
                "verbose_name_plural": "eShipper XML Settings",
            },
        ),
        migrations.AlterModelTable(
            name="eshipperxmlsettings",
            table="eshipper-xml-settings",
        ),
    ]