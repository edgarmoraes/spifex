import openpyxl
from .forms import AccountForm
from django.db import transaction
from .forms import UploadFileForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Chart_of_accounts
from realizado.models import Tabela_realizado
from fluxo_de_caixa.models import Tabela_fluxo
from django.shortcuts import render, redirect, get_object_or_404

def upload_and_save(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            worksheet = wb.active

            # Verification (replace with your actual verification logic)
            if (worksheet['XFD1'].value != "sppiff" or
                    worksheet['XFD2'].value != "1ccd101b-aed4-4b56-b852-02c8ce8a6f70" or
                    worksheet['XFD3'].value != "a5296f55-e314-48d2-8415-f0204d3162f8"):
                messages.error(request, 'A planilha não passou na verificação de segurança.')
                return redirect('/plano_de_contas/')  # Replace with your upload URL

            # Check for used accounts
            used_accounts = set(
                Tabela_fluxo.objects.filter(conta_contabil__in=Chart_of_accounts.objects.values_list('account', flat=True))
                .values_list('conta_contabil', flat=True)
            ).union(
                Tabela_realizado.objects.filter(conta_contabil__in=Chart_of_accounts.objects.values_list('account', flat=True))
                .values_list('conta_contabil', flat=True)
            )

            if used_accounts:
                messages.error(request, f'As seguintes contas estão sendo utilizadas: {", ".join(used_accounts)}')
                return redirect('/plano_de_contas/')  # Replace with your upload URL

            # Import logic
            with transaction.atomic():
                Chart_of_accounts.objects.all().delete()  # Delete existing accounts

                objects_to_create = []
                for row in worksheet.iter_rows(min_row=2, values_only=True):
                    if row[1] is None:
                        continue
                    objects_to_create.append(
                        Chart_of_accounts(
                            nature=row[0] or '',
                            group=row[1] or '',
                            subgroup=row[2] or '',
                            account=row[3] or ''
                        )
                    )
                Chart_of_accounts.objects.bulk_create(objects_to_create)

    else:
        form = UploadFileForm()

    chart_of_accounts = Chart_of_accounts.objects.all().order_by('-group')
    return render(request, 'chart_of_accounts.html', {'form': form, 'chart_of_accounts': chart_of_accounts})

def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta adicionada com sucesso!')
            return redirect('plano_de_contas:plano_de_contas')
        else:
            print(form.errors)  # Isso ajudará a ver os erros no console do servidor
    else:
        form = AccountForm()
    return render(request, 'add_account_form.html', {'form': form})

def get_groups(request):
    groups = Chart_of_accounts.objects.values('group').distinct()
    groups_with_nature = [
        {'name': group['group'], 'nature': 'Crédito' if group['group'] in ['Receitas Operacionais', 'Receitas Não Operacionais'] else 'Débito'}
        for group in groups
    ]
    return JsonResponse(groups_with_nature, safe=False)

def get_subgroups(request):
    group = request.GET.get('group')
    nature = request.GET.get('nature')
    subgroups = Chart_of_accounts.objects.filter(group=group, nature=nature).values_list('subgroup', flat=True).distinct()
    return JsonResponse(list(subgroups), safe=False)

def edit_account(request, account_id):
    # Busca a conta pelo ID ou retorna 404 se não encontrada
    account = get_object_or_404(Chart_of_accounts, id=account_id)
    
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta atualizada com sucesso!')
        account_uuid = account.uuid
        Tabela_realizado.objects.filter(uuid_conta_contabil=account_uuid).update(conta_contabil=account.account)
        Tabela_fluxo.objects.filter(uuid_conta_contabil=account_uuid).update(conta_contabil=account.account)

        return redirect('plano_de_contas:plano_de_contas')
    else:
        form = AccountForm(instance=account)
    
    return render(request, 'edit_account_form.html', {'form': form, 'account_id': account_id})

def delete_account(request, account_id):
    account = get_object_or_404(Chart_of_accounts, id=account_id)

    # Check if the account is used in other models
    if Tabela_fluxo.objects.filter(uuid_conta_contabil=account.uuid).exists() or \
       Tabela_realizado.objects.filter(uuid_conta_contabil=account.uuid).exists():
        messages.error(request, 'Esta conta está sendo utilizada e não pode ser excluída.')
        return redirect('plano_de_contas:edit_account', account_id)

    # If not used, delete the account
    account.delete()
    messages.success(request, 'Conta excluída com sucesso!')
    return redirect('plano_de_contas:plano_de_contas')