# Generated by Django 2.0.6 on 2018-08-23 16:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalparticipante',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical Participante'},
        ),
        migrations.AlterModelOptions(
            name='participante',
            options={'ordering': ('asn',), 'verbose_name': 'Participante', 'verbose_name_plural': 'Participantes'},
        ),
        migrations.RemoveField(
            model_name='contrato',
            name='template_path',
        ),
        migrations.RemoveField(
            model_name='contrato',
            name='template_valores_antigos',
        ),
        migrations.AddField(
            model_name='contrato',
            name='template_en',
            field=models.CharField(blank=True, max_length=25000, null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='template_pt',
            field=models.CharField(blank=True, max_length=25000, null=True),
        ),
        migrations.AlterField(
            model_name='historicalparticipante',
            name='asn',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='historicalparticipante',
            name='endereco_bairro',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='historicalparticipante',
            name='endereco_cep',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='historicalparticipante',
            name='endereco_numero',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='historicalparticipante',
            name='endereco_rua',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='historicalparticipante',
            name='telefone_ddd',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='asn',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='participante',
            name='endereco_bairro',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='endereco_cep',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='endereco_numero',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='endereco_rua',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='participante',
            name='perfil',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='participantes', related_query_name='participante', to='core.PerfilParticipante'),
        ),
        migrations.AlterField(
            model_name='participante',
            name='telefone_ddd',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
