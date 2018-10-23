# Generated by Django 2.0.8 on 2018-08-21 14:55

import dirtyfields.dirtyfields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import invoice_api.core.validators
import simple_history.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('assinado', models.BooleanField()),
                ('data_assinatura', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('template_path', models.CharField(max_length=30, null=True)),
                ('template_valores_antigos', models.TextField(null=True)),
                ('tipo', models.CharField(max_length=30)),
                ('vigente', models.BooleanField()),
                ('usuario', models.CharField(max_length=30)),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Contrato',
                'verbose_name_plural': 'Contratos',
                'ordering': ('-data_assinatura',),
            },
        ),
        migrations.CreateModel(
            name='Fatura',
            fields=[
                ('boleto_gerado', models.BooleanField()),
                ('boleto_url', models.CharField(error_messages={'invalid': 'Insira uma url válida.'}, max_length=255, null=True, validators=[django.core.validators.URLValidator()])),
                ('data_fatura_gerada', models.DateField(default=django.utils.timezone.now, editable=False)),
                ('encerrada', models.BooleanField()),
                ('estado', models.CharField(max_length=30)),
                ('id_financeiro', models.BigIntegerField()),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('valor', models.FloatField()),
                ('vencimento', models.DateField()),
            ],
            options={
                'verbose_name': 'Fatura',
                'verbose_name_plural': 'Faturas',
                'ordering': ('-vencimento',),
            },
        ),
        migrations.CreateModel(
            name='HistoricalParticipante',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4)),
                ('asn', models.IntegerField()),
                ('razao_social', models.CharField(blank=True, max_length=150, null=True)),
                ('cnpj', models.CharField(blank=True, max_length=14, null=True, validators=[invoice_api.core.validators.validacao_cnpj])),
                ('responsavel', models.CharField(blank=True, max_length=150, null=True)),
                ('endereco_rua', models.CharField(max_length=100)),
                ('endereco_numero', models.CharField(max_length=10)),
                ('endereco_complemento', models.CharField(blank=True, max_length=45)),
                ('endereco_bairro', models.CharField(max_length=45)),
                ('endereco_cep', models.CharField(blank=True, max_length=45, null=True)),
                ('endereco_cidade', models.CharField(blank=True, max_length=45, null=True)),
                ('endereco_estado', models.CharField(blank=True, max_length=2, null=True)),
                ('telefone_ddd', models.CharField(max_length=2)),
                ('telefone_numero', models.CharField(blank=True, max_length=150, null=True)),
                ('telefone_ramal', models.CharField(blank=True, max_length=5, null=True)),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical participante',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='IX',
            fields=[
                ('cidade', models.CharField(max_length=45)),
                ('codigo', models.CharField(max_length=4)),
                ('estado', models.CharField(max_length=4)),
                ('ix_id', models.IntegerField(primary_key=True, serialize=False)),
                ('nome_curto', models.CharField(max_length=16, verbose_name='Nome Curto')),
                ('nome_longo', models.CharField(max_length=48, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'IX',
                'verbose_name_plural': 'IXs',
                'ordering': ('codigo',),
            },
        ),
        migrations.CreateModel(
            name='Participante',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('asn', models.IntegerField()),
                ('razao_social', models.CharField(blank=True, max_length=150, null=True)),
                ('cnpj', models.CharField(blank=True, max_length=14, null=True, validators=[invoice_api.core.validators.validacao_cnpj])),
                ('responsavel', models.CharField(blank=True, max_length=150, null=True)),
                ('endereco_rua', models.CharField(max_length=100)),
                ('endereco_numero', models.CharField(max_length=10)),
                ('endereco_complemento', models.CharField(blank=True, max_length=45)),
                ('endereco_bairro', models.CharField(max_length=45)),
                ('endereco_cep', models.CharField(blank=True, max_length=45, null=True)),
                ('endereco_cidade', models.CharField(blank=True, max_length=45, null=True)),
                ('endereco_estado', models.CharField(blank=True, max_length=2, null=True)),
                ('telefone_ddd', models.CharField(max_length=2)),
                ('telefone_numero', models.CharField(blank=True, max_length=150, null=True)),
                ('telefone_ramal', models.CharField(blank=True, max_length=5, null=True)),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
            ],
            options={
                'ordering': ('asn',),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PerfilParticipante',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('tipo', models.CharField(max_length=30)),
                ('fator_de_desconto', models.FloatField(default=0.0, error_messages={'max_value': 'Insira um valor de desconto válido. Certifique-se de que a entrada esteja entre 0 e 100.', 'min_value': 'Insira um valor de desconto válido. Certifique-se de que a entrada esteja entre 0 e 100.'}, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
            ],
            options={
                'verbose_name': 'PerfilParticipante',
                'verbose_name_plural': 'PerfisParticipantes',
                'ordering': ('fator_de_desconto',),
            },
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('data_expiracao', models.DateTimeField()),
                ('hash', models.CharField(max_length=30)),
                ('preco', models.FloatField(default=0.0, error_messages={'min_value': 'Insira uma preço válido.'}, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('recorrente', models.BooleanField()),
                ('tipo', models.CharField(max_length=255)),
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('ix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicos', related_query_name='servico', to='core.IX')),
                ('participante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='servicos', related_query_name='servico', to='core.Participante')),
            ],
            options={
                'verbose_name': 'Servico',
                'verbose_name_plural': 'Servicos',
                'ordering': ('participante', 'data_expiracao'),
            },
        ),
        migrations.CreateModel(
            name='OrdemDeCompra',
            fields=[
                ('fatura', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ordem_compra', related_query_name='ordem_compra', serialize=False, to='core.Fatura')),
                ('identificacao_oc', models.CharField(max_length=30)),
                ('url', models.CharField(error_messages={'invalid': 'Insira uma url válida.'}, max_length=255, null=True)),
            ],
            options={
                'verbose_name': 'OrdemDeCompra',
                'verbose_name_plural': 'OrdensDeCompra',
                'ordering': ('-identificacao_oc',),
            },
        ),
        migrations.AddField(
            model_name='participante',
            name='perfil',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.PerfilParticipante'),
        ),
        migrations.AddField(
            model_name='historicalparticipante',
            name='perfil',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.PerfilParticipante'),
        ),
        migrations.AddField(
            model_name='fatura',
            name='participante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faturas', related_query_name='fatura', to='core.Participante'),
        ),
        migrations.AddField(
            model_name='fatura',
            name='servicos',
            field=models.ManyToManyField(related_name='faturas', related_query_name='fatura', to='core.Servico'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='ix',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contratos', related_query_name='contrato', to='core.IX'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='participante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contratos', related_query_name='contrato', to='core.Participante'),
        ),
    ]