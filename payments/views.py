from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from .models import Payment
from billing.models import Invoice, Service
from zone.models import Worker





@login_required
def payment_list(request):
    """List all payments with search and filtering"""
    from django.db.models import Sum, Count
    
    payments = Payment.objects.select_related('invoice', 'created_by').order_by('-payment_date', '-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(payment_number__icontains=search) |
            Q(invoice_number__icontains=search) |
            Q(reference_number__icontains=search) |
            Q(invoice__client_name__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        payments = payments.filter(status=status)
    
    # Filter by payment method
    method = request.GET.get('method')
    if method:
        payments = payments.filter(payment_method=method)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    
    # Calculate statistics for the filtered payments
    stats = payments.aggregate(
        total_amount=Sum('amount'),
        completed_count=Count('id', filter=Q(status='completed')),
        pending_count=Count('id', filter=Q(status='pending')),
        failed_count=Count('id', filter=Q(status='failed'))
    )
    
    # Calculate average payment amount
    total_count = payments.count()
    avg_amount = (stats['total_amount'] / total_count) if total_count > 0 and stats['total_amount'] else 0
    
    # Pagination
    paginator = Paginator(payments, 25)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    context = {
        'title': 'All Payments',
        'payments': payments,
        'search': search,
        'selected_status': status,
        'selected_method': method,
        'date_from': date_from,
        'date_to': date_to,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
        'status_choices': Payment._meta.get_field('status').choices,
        # Statistics
        'total_amount': stats['total_amount'] or 0,
        'completed_count': stats['completed_count'] or 0,
        'pending_count': stats['pending_count'] or 0,
        'failed_count': stats['failed_count'] or 0,
        'avg_amount': avg_amount,
    }
    return render(request, 'payments/payment_list.html', context)


@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'title': f'Payment {payment.payment_number}',
        'payment': payment,
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_create(request):
    """Create a new payment"""
    if request.method == 'POST':
        # Handle form submission
        invoice_id = request.POST.get('invoice_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        reference_number = request.POST.get('reference_number')
        notes = request.POST.get('notes')
        
        try:
            invoice = None
            if invoice_id:
                invoice = Invoice.objects.get(id=invoice_id)
            
            payment = Payment.objects.create(
                invoice=invoice,
                invoice_number=request.POST.get('invoice_number', ''),
                amount=amount,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
                created_by=request.user
            )
            
            messages.success(request, f'Payment {payment.payment_number} recorded successfully.')
            return redirect('payments:payment_detail', payment_id=payment.id)
            
        except Exception as e:

            
            pass
            messages.error(request, f'Error creating payment: {str(e)}')
    
    # Get recent invoices for selection
    recent_invoices = Invoice.objects.filter(status='pending').order_by('-created_at')[:20]
    
    context = {
        'title': 'Record New Payment',
        'recent_invoices': recent_invoices,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_edit(request, payment_id):
    """Edit an existing payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        try:
            payment.amount = request.POST.get('amount')
            payment.payment_method = request.POST.get('payment_method')
            payment.reference_number = request.POST.get('reference_number')
            payment.notes = request.POST.get('notes')
            payment.save()
            
            messages.success(request, f'Payment {payment.payment_number} updated successfully.')
            return redirect('payments:payment_detail', payment_id=payment.id)
            
        except Exception as e:

            
            pass
            messages.error(request, f'Error updating payment: {str(e)}')
    
    context = {
        'title': f'Edit Payment {payment.payment_number}',
        'payment': payment,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'payments/payment_form.html', context)


@login_required
def payment_delete(request, payment_id):
    """Delete a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if request.method == 'POST':
        payment_number = payment.payment_number
        payment.delete()
        messages.success(request, f'Payment {payment_number} deleted successfully.')
        return redirect('payments:payment_list')
    
    context = {
        'title': f'Delete Payment {payment.payment_number}',
        'payment': payment,
    }
    return render(request, 'payments/payment_delete.html', context)


@login_required
def payment_receipt(request, payment_id):
    """Generate receipt for a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{payment.payment_number}.pdf"'
    
    # Create the PDF object using BytesIO as a file-like buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"PAYMENT RECEIPT", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Payment details
    details_data = [
        ['Receipt Number:', payment.payment_number],
        ['Payment Date:', payment.payment_date.strftime('%B %d, %Y')],
        ['Payment Method:', payment.get_payment_method_display()],
        ['Amount:', f"${payment.amount:.2f}"],
        ['Status:', payment.get_status_display()],
    ]
    
    if payment.reference_number:
        details_data.append(['Reference:', payment.reference_number])
    
    if payment.invoice:
        details_data.append(['Invoice:', payment.invoice.invoice_number])
        details_data.append(['Client:', payment.invoice.get_client_name()])
    
    details_table = Table(details_data, colWidths=[2*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(details_table)
    
    if payment.notes:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Notes:</b> {payment.notes}", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
def invoice_payment(request, invoice_id):
    """Create payment for a specific invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        try:
            payment = Payment.objects.create(
                invoice=invoice,
                invoice_number=invoice.invoice_number,
                amount=request.POST.get('amount'),
                payment_method=request.POST.get('payment_method'),
                reference_number=request.POST.get('reference_number'),
                notes=request.POST.get('notes'),
                created_by=request.user
            )
            
            messages.success(request, f'Payment {payment.payment_number} recorded for invoice {invoice.invoice_number}.')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
            
        except Exception as e:

            
            pass
            messages.error(request, f'Error recording payment: {str(e)}')
    
    context = {
        'title': f'Record Payment for Invoice {invoice.invoice_number}',
        'invoice': invoice,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'payments/invoice_payment.html', context)


@login_required
def payment_reports(request):
    """Payment reports dashboard"""
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Monthly payment data for the last 12 months
    monthly_data = []
    for i in range(12):
        month_start = (this_month - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        amount = Payment.objects.filter(
            status='completed',
            payment_date__gte=month_start,
            payment_date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'amount': amount
        })
    
    monthly_data.reverse()  # Show oldest to newest
    
    # Payment method breakdown
    method_breakdown = Payment.objects.filter(
        status='completed',
        payment_date__gte=this_month
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'title': 'Payment Reports',
        'monthly_data': monthly_data,
        'method_breakdown': method_breakdown,
    }
    return render(request, 'payments/reports.html', context)


@login_required
def daily_collection_report(request):
    """Daily payment collection report"""
    date = request.GET.get('date', timezone.now().date())
    if isinstance(date, str):
        date = datetime.strptime(date, '%Y-%m-%d').date()
    
    payments = Payment.objects.filter(
        status='completed',
        payment_date=date
    ).select_related('invoice')
    
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'title': f'Daily Collection Report - {date.strftime("%B %d, %Y")}',
        'date': date,
        'payments': payments,
        'total_amount': total_amount,
    }
    return render(request, 'payments/daily_report.html', context)


@login_required
def monthly_payment_report(request):
    """Monthly payment report"""
    month = request.GET.get('month', timezone.now().strftime('%Y-%m'))
    year, month_num = month.split('-')
    month_start = datetime(int(year), int(month_num), 1).date()
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    payments = Payment.objects.filter(
        status='completed',
        payment_date__gte=month_start,
        payment_date__lte=month_end
    ).select_related('invoice')
    
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'title': f'Monthly Payment Report - {month_start.strftime("%B %Y")}',
        'month': month,
        'month_start': month_start,
        'month_end': month_end,
        'payments': payments,
        'total_amount': total_amount,
    }
    return render(request, 'payments/monthly_report.html', context)


# AJAX endpoints
@login_required
def get_invoice_balance(request, invoice_id):
    """Get invoice balance via AJAX"""
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        return JsonResponse({
            'balance': float(invoice.balance_due),
            'total': float(invoice.total_amount),
            'paid': float(invoice.total_paid)
        })
    except Invoice.DoesNotExist:
        return JsonResponse({'error': 'Invoice not found'}, status=404)


@login_required
def update_payment_status(request, payment_id):
    """Update payment status via AJAX"""
    if request.method == 'POST':
        try:
            payment = Payment.objects.get(id=payment_id)
            new_status = request.POST.get('status')
            
            if new_status in [choice[0] for choice in Payment._meta.get_field('status').choices]:
                payment.status = new_status
                payment.save()
                return JsonResponse({'success': True, 'status': payment.get_status_display()})
            else:
                return JsonResponse({'error': 'Invalid status'}, status=400)
                
        except Payment.DoesNotExist:

                
            pass
            return JsonResponse({'error': 'Payment not found'}, status=404)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
