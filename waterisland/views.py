from django.http import HttpResponse
from django.shortcuts import render, redirect
from waterisland.models import *
import pandas as pd
from django import template
from django.db import connections, transaction
from django.core.cache import cache

GS = 1
SSB = 2
register = template.Library()


def balance_upload_handler(file_name, trader_balances):
    if file_name == 'traderBalances':
        row_count = trader_balances.shape[0]
        v = ''
        for i in range(0, row_count):
            r = trader_balances.iloc[i]
            x, vendor, currency = r.name
            if not pd.isna(vendor) and str(vendor) == 'SSB':
                v = 'SSB'
            elif not pd.isna(vendor) and str(vendor) == 'GS':
                v = 'GS'
            if not pd.isna(currency):
                s = trader_balances.iloc[i + 1]
                if v == 'SSB':
                    Balances.objects.get_or_create(vendor=SSB, currency=str(currency).strip())
                    b = Balances.objects.get(vendor=SSB, currency=str(currency).strip())
                    b.trader_balance = s['Balance']
                    b.save()
                    i += 1
                elif v == 'GS':
                    Balances.objects.get_or_create(vendor=GS, currency=str(currency))
                    b = Balances.objects.get(vendor=GS, currency=str(currency))
                    b.trader_balance = s['Balance']
                    b.save()
                    i += 1
    elif file_name == 'ssbBalances':
        ssb_balance = trader_balances.dropna()
        for i in range(0, ssb_balance.shape[0]):
            r = ssb_balance.iloc[i]
            Balances.objects.get_or_create(vendor=SSB, currency=str(r['Currency']).strip())
            b = Balances.objects.get(vendor=SSB, currency=str(r['Currency']).strip())
            b.balance = r['Amount']
            b.save()
    elif file_name == 'gsBalances':
        gs_balance = trader_balances[trader_balances['Unnamed: 6'] == 'LG']
        for i in range(0, gs_balance.shape[0]):
            r = gs_balance.iloc[i]
            Balances.objects.get_or_create(vendor=GS, currency=str(r['Unnamed: 2']))
            b = Balances.objects.get(vendor=GS, currency=str(r['Unnamed: 2']))
            b.balance = r['Unnamed: 4']
            b.save()
    f = AllFiles.objects.get(value=file_name)
    f.uploaded = 1
    f.save()


def transaction_upload_handler(file_name, df):
    if file_name == 'traderTransactions':
        trader_transactions = df[df['Fund'] == 'LG']
        for i in range(0, trader_transactions.shape[0]):
            r = trader_transactions.iloc[i]
            account = GS
            if r['Account'] == "SS":
                account = SSB
            institution = Institutions.objects.filter(code__contains=str(r['Ticker']).split()[0]).first()
            if institution:
                t = Transactions.objects.get_or_create(vendor=account,
                                                       date=r['Date'],
                                                       institution=institution)
                t = t[0]
                t.trader_total = float(t.trader_total) + r['Cashflow']
                t.save()
            else:
                i = Institutions.objects.create(institution=r['Description'], code=str(r['Ticker']).split()[0])
                Transactions.objects.get_or_create(vendor=account,
                                                   date=r['Date'],
                                                   institution=i,
                                                   trader_total=r['Cashflow'])
    elif file_name == 'gsTransactions':
        gs_transactions = df[df['Fund'] == 'LITMAN GREGORY']
        gs_transactions = gs_transactions[gs_transactions['TradeDate'].notnull()]
        gs_transactions['Date'] = pd.to_datetime(gs_transactions['TradeDate'])
        for i in range(0, gs_transactions.shape[0]):
            r = gs_transactions.iloc[i]
            institution = Institutions.objects.filter(code__contains=r['ProductID']).first()
            if institution:
                t = Transactions.objects.get_or_create(vendor=GS,
                                                       date=r['Date'],
                                                       institution=institution)
                t = t[0]
                t.total = float(t.total) + r['NetAmount']
                t.save()
            else:
                i = Institutions.objects.create(institution=r['Product Description'], code=r['ProductID'])
                Transactions.objects.get_or_create(vendor=GS,
                                                   date=r['Date'],
                                                   institution=i,
                                                   total=r['NetAmount'])
    elif file_name == 'ssbTransactions':
        ssb_transactions = df[df['Ticker'].notnull()]
        for i in range(0, ssb_transactions.shape[0]):
            r = ssb_transactions.iloc[i]
            institution = Institutions.objects.filter(code__contains=r['Ticker']).first()
            if institution:
                t = Transactions.objects.get_or_create(vendor=SSB,
                                                       date=r['Trade/Record Date'],
                                                       institution=institution)
                t = t[0]
                t.total = float(t.total) + r['Net Amount']
                t.save()
            else:
                i = Institutions.objects.create(institution=r['Security Name'], code=r['Ticker'])
                Transactions.objects.get_or_create(vendor=SSB,
                                                   date=r['Trade/Record Date'],
                                                   institution=i,
                                                   total=r['Net Amount'])
    f = AllFiles.objects.get(value=file_name)
    f.uploaded = 1
    f.save()


def upload_balances(request):
    alert = False
    if request.POST:
        myfile = request.FILES['fileUpload']
        file_name = request.POST.get('fileName')
        if str(file_name).find("Balances") != -1:
            balance_upload_handler(file_name, pd.read_excel(myfile))
        else:
            transaction_upload_handler(file_name, pd.read_excel(myfile))
        alert = True
    remaining_files = AllFiles.objects.filter(uploaded=0)
    all_files = AllFiles.objects.all()
    return render(request, "uploads.html", {'remaining_files': remaining_files, 'all_files': all_files, 'alert': alert})


def clear_database(request):
    print("ALERT - CLEARING DB")
    cache.clear()
    Transactions.objects.all().delete()
    Balances.objects.all().delete()
    Institutions.objects.all().delete()
    AllFiles.objects.all().update(uploaded=0)
    return redirect('/upload')


def currency_matching(request):
    all_uploaded_files = AllFiles.objects.filter(uploaded=1)
    total = 0
    for f in all_uploaded_files:
        if f.value == 'traderBalances' or f.value == 'ssbBalances' or f.value == 'gsBalances':
            total += 1
    error = total != 3
    ssb = None
    gs = None
    if not error:
        ssb = Balances.objects.filter(vendor=SSB)
        gs = Balances.objects.filter(vendor=GS)
    return render(request, "currency.html", {'error': error, 'ssb': ssb, 'gs': gs})


def institution_matching(request):
    all_uploaded_files = AllFiles.objects.filter(uploaded=1)
    total = 0
    for f in all_uploaded_files:
        if f.value == 'traderTransactions' or f.value == 'gsTransactions' or f.value == 'ssbTransactions':
            total += 1
    error = total != 3
    ssb = None
    gs = None
    if not error:
        ssb = Transactions.objects.filter(vendor=SSB)
        gs = Transactions.objects.filter(vendor=GS)
    return render(request, "institution.html", {'error': error, 'ssb': ssb, 'gs': gs})


def test(request):
    return render(request, "test.html")


def transaction_detail(request, id):
    transaction = Transactions.objects.filter(id=id).first()
    alert = False
    if request.POST:
        comments = request.POST.get("comments")
        transaction.comments = comments
        transaction.save()
        alert = True
    account = 'GS' if transaction.vendor == GS else 'SSB'
    total = transaction.total
    trader_total = transaction.trader_total
    exception = abs(total - trader_total)
    status = 'matched' if trader_total == total else 'not matched'
    status_class = 'matched-transaction' if trader_total == total else 'unmatched-transaction'
    date = transaction.date
    idx = transaction.id
    comments = transaction.comments or ''
    return render(request, "transactiondetail.html", {'account': account,
                                                      'total': total,
                                                      'trader_total': trader_total,
                                                      'exception': exception,
                                                      'status': status,
                                                      'date': date,
                                                      'status_class': status_class,
                                                      'idx': idx,
                                                      'comments': comments,
                                                      'alert': alert})
