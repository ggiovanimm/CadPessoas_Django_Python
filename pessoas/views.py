from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Pessoa
from .forms import PessoaForm
import plotly.express as px
from django.utils import timezone
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


# Listar pessoas
from django.db.models import Count

def pessoa_list(request):
    # Obter todos os cadastros
    pessoas = Pessoa.objects.all()

    # Obter a quantidade de cadastros por dia
    cadastros_por_dia = (
        Pessoa.objects
        .values('data_registro')  # Agrupar por data completa
        .annotate(quantidade=Count('id'))  # Contar cadastros por data
        .order_by('data_registro')  # Ordenar por data
    )

    # Extrair datas e quantidades para o gráfico
    datas = [cadastro['data_registro'] for cadastro in cadastros_por_dia]  # Usar o valor diretamente
    quantidades = [cadastro['quantidade'] for cadastro in cadastros_por_dia]

    # Gráfico Plotly
    fig = px.bar(x=datas, y=quantidades, labels={'x': 'Data', 'y': 'Quantidade'})

    # Ajustar a largura das colunas
    fig.update_layout(bargap=0.8)  # Ajuste o valor conforme necessário

    # Formatar o eixo X para mostrar apenas a data
    # Definir os ticks do eixo X para exibir apenas as datas que têm barras
    fig.update_xaxes(tickvals=datas, ticktext=[date.strftime('%Y-%m-%d') for date in datas])  # Formato desejado para a data

    plot_div = fig.to_html(full_html=False)
    
    return render(request, 'pessoas/pessoa_list.html', {'pessoas': pessoas, 'plot_div': plot_div})


# Criar nova pessoa
def pessoa_create(request):
    if request.method == 'POST':
        form = PessoaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pessoa_list')
    else:
        form = PessoaForm()
    return render(request, 'pessoas/pessoa_form.html', {'form': form})

# Editar pessoa
def pessoa_update(request, pk):
    pessoa = Pessoa.objects.get(id=pk)
    if request.method == 'POST':
        form = PessoaForm(request.POST, instance=pessoa)
        if form.is_valid():
            form.save()
            return redirect('pessoa_list')
    else:
        form = PessoaForm(instance=pessoa)
    return render(request, 'pessoas/pessoa_form.html', {'form': form})

# Deletar pessoa
def pessoa_delete(request, pk):
    pessoa = Pessoa.objects.get(id=pk)
    if request.method == 'POST':
        pessoa.delete()
        return redirect('pessoa_list')
    return render(request, 'pessoas/pessoa_confirm_delete.html', {'pessoa': pessoa})

# Resumo da pessoa
def pessoa_resumo(request, pk):
    pessoa = Pessoa.objects.get(id=pk)
    return render(request, 'pessoas/pessoa_resumo.html', {'pessoa': pessoa})

def render_pdf_view(request, pessoa_id):
    # Obter a pessoa com base no ID
    pessoa = Pessoa.objects.get(id=pessoa_id)
    
    # Renderizar o template HTML específico para PDF
    html = render_to_string('pessoas/pessoa_resumo_pdf.html', {'pessoa': pessoa})

    # Criação do PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pessoa_{pessoa_id}.pdf"'

    # Converter HTML para PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Verificar se houve erros na criação do PDF
    if pisa_status.err:
        return HttpResponse('Erro ao criar PDF', status=400)

    return response

def gerar_pdf(request):
    # Criar a resposta HTTP para o PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cadastros.pdf"'

    # Criar um documento PDF
    doc = SimpleDocTemplate(response, pagesize=letter)

    # Obter todos os registros de pessoas
    pessoas = Pessoa.objects.all()

    # Criar os dados da tabela
    dados = [['Nome', 'CPF', 'Celular', 'E-mail']]  # Cabeçalho da tabela
    for pessoa in pessoas:
        dados.append([pessoa.nome, pessoa.cpf, pessoa.celular, pessoa.email])

    # Criar a tabela
    tabela = Table(dados)

    # Estilizar a tabela
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    tabela.setStyle(estilo)

    # Construir o PDF
    elementos = [tabela]
    doc.build(elementos)

    return response

def export_csv(request):
    # Cria a resposta com o tipo de conteúdo como CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cadastros.csv"'

    # Define a codificação para o escritor CSV
    response.write('\ufeff'.encode('utf-8'))  # Adiciona BOM para UTF-8

    # Cria um escritor CSV
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Nome', 'CPF', 'Celular', 'Email', 'Endereço', 'Bairro', 'Cidade', 'Estado', 'Data de Registro'])  # Cabeçalhos

    # Obter todos os cadastros
    pessoas = Pessoa.objects.all().values_list('nome', 'cpf', 'celular', 'email', 'endereco', 'bairro', 'cidade', 'estado', 'data_registro')

     # Adiciona cada pessoa ao CSV
    for pessoa in pessoas:
        writer.writerow(pessoa)

    return response


