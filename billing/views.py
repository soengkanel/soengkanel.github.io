from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from cards.models import WorkerIDCard
from user_management.models import UserRoleAssignment

from .models import CashChequeReceipt, Invoice, InvoiceLineItem, Service, ServiceHistory
from .forms import (
    CashChequeReceiptForm, InvoiceForm, InvoiceLineItemFormSet, ServiceForm, 
    InvoiceSearchForm, ServiceSearchForm
)
from zone.models import Worker


@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def billing_dashboard(request):
    """Enhanced billing dashboard with key metrics and recent activity"""
    try:
        from .models import OfficialReceipt, CashChequeReceipt, PaymentVoucher
        receipts_available = True
    except ImportError:
        receipts_available = False
    
    # Calculate dashboard metrics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Revenue metrics
    total_revenue = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid', 
        issue_date__gte=this_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Outstanding metrics
    pending_amount = Invoice.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    overdue_count = Invoice.objects.filter(
        status='pending',
        due_date__lt=today
    ).count()
    
    # Invoice workflow metrics
    total_invoices_amount = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    draft_invoices_amount = Invoice.objects.filter(status='draft').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    pending_approval_invoices_amount = Invoice.objects.filter(status='pending_approval').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    approved_invoices_amount = Invoice.objects.filter(status='approved').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Receipt metrics (if available)
    total_receipts = 0
    total_vouchers = 0
    total_vouchers_amount = 0
    pending_vouchers_amount = 0
    approved_vouchers_amount = 0
    paid_vouchers_amount = 0
    recent_receipts = []
    recent_vouchers = []
    
    if receipts_available:
        try:
            total_receipts = OfficialReceipt.objects.count() + CashChequeReceipt.objects.count()
            recent_receipts = OfficialReceipt.objects.order_by('-created_at')[:5]
        except:
            total_receipts = 0
            recent_receipts = []
        
        try:
            total_vouchers = PaymentVoucher.objects.count()
            total_vouchers_amount = PaymentVoucher.objects.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
            pending_vouchers_amount = PaymentVoucher.objects.filter(status__in=['draft', 'pending_approval']).aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
            approved_vouchers_amount = PaymentVoucher.objects.filter(status='approved').aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
            paid_vouchers_amount = PaymentVoucher.objects.filter(status='paid').aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
            recent_vouchers = PaymentVoucher.objects.order_by('-created_at')[:5]
        except:
            total_vouchers = 0
            total_vouchers_amount = 0
            pending_vouchers_amount = 0
            approved_vouchers_amount = 0
            paid_vouchers_amount = 0
            recent_vouchers = []
    
    # Recent invoices
    recent_invoices = Invoice.objects.select_related('worker').order_by('-created_at')[:5]
    
    # Monthly comparison
    last_month_revenue = Invoice.objects.filter(
        status='paid',
        issue_date__gte=last_month,
        issue_date__lt=this_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    revenue_change = 0
    if last_month_revenue > 0:
        revenue_change = ((monthly_revenue - last_month_revenue) / last_month_revenue) * 100
    
    context = {
        'title': 'Billing Dashboard',
        'total_invoices': Invoice.objects.count(),
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'pending_count': Invoice.objects.filter(status='pending').count(),
        'pending_amount': pending_amount,
        'overdue_count': overdue_count,
        'total_receipts': total_receipts,
        'total_vouchers': total_vouchers,
        'total_vouchers_amount': total_vouchers_amount,
        'pending_vouchers_amount': pending_vouchers_amount,
        'approved_vouchers_amount': approved_vouchers_amount,
        'paid_vouchers_amount': paid_vouchers_amount,
        # Invoice workflow metrics
        'total_invoices_amount': total_invoices_amount,
        'draft_invoices_amount': draft_invoices_amount,
        'pending_approval_invoices_amount': pending_approval_invoices_amount,
        'approved_invoices_amount': approved_invoices_amount,
        'recent_invoices': recent_invoices,
        'recent_receipts': recent_receipts,
        'recent_vouchers': recent_vouchers,
        'revenue_change': revenue_change,
        'revenue_trend': 'up' if revenue_change > 0 else 'down' if revenue_change < 0 else 'same',
    }
    return render(request, 'billing/dashboard.html', context)


@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def invoice_list(request):
    """List all invoices with search and filtering"""
    form = InvoiceSearchForm(request.GET)
    invoices = Invoice.objects.select_related('worker').order_by('-created_at')
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            invoices = invoices.filter(
                Q(invoice_number__icontains=search) |
                Q(client_name__icontains=search) |
                Q(worker__first_name__icontains=search) |
                Q(worker__last_name__icontains=search)
            )
        
        status = form.cleaned_data.get('status')
        if status:
            invoices = invoices.filter(status=status)
        
        client_type = form.cleaned_data.get('client_type')
        if client_type == 'worker':
            invoices = invoices.filter(worker__isnull=False)
        elif client_type == 'other':
            invoices = invoices.filter(worker__isnull=True)
        
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            invoices = invoices.filter(issue_date__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            invoices = invoices.filter(issue_date__lte=date_to)
    
    # Pagination
    paginator = Paginator(invoices, 20)
    page = request.GET.get('page')
    invoices = paginator.get_page(page)
    
    context = {
        'title': 'All Invoices',
        'invoices': invoices,
        'form': form,
    }
    return render(request, 'billing/invoice_list.html', context)


@login_required
@permission_required('billing.add_invoice', raise_exception=True)
def invoice_create(request):
    """Create a new invoice"""
    role = UserRoleAssignment.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        formset = InvoiceLineItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()
            
            formset.instance = invoice
            formset.save()
            
            # Recalculate totals
            invoice.calculate_totals()
            invoice.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
        formset = InvoiceLineItemFormSet()
    
    
    context = {
        'title': 'Create Invoice',
        'form': form,
        'formset': formset,
        'invoice': None,  # For new invoices
        'status_choices': Invoice.STATUS_CHOICES,
        'submit_text': 'Create Invoice',
        'role':role
    }
    return render(request, 'billing/invoice_form.html', context)


@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def invoice_detail(request, invoice_id):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    line_items = invoice.line_items.all()
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    card = None
    if invoice.worker:
        card = WorkerIDCard.objects.filter(
            worker=invoice.worker
        ).first()
    # Calculate role-based permissions for template
    can_approve = invoice.can_approve(request.user)
    can_reject = invoice.can_reject(request.user)
    can_submit = invoice.can_submit_for_approval() and invoice.created_by == request.user
    can_send_to_client = invoice.status == 'approved'
    
    context = {
        'title': f'Invoice {invoice.invoice_number}',
        'invoice': invoice,
        'line_items': line_items,
        'can_approve': can_approve,
        'can_reject': can_reject,
        'can_submit': can_submit,
        'can_send_to_client': can_send_to_client,
        'card':card,
        'role':role
    }
    return render(request, 'billing/invoice_detail.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def invoice_edit(request, invoice_id):
    """Edit an existing invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES, instance=invoice)
        formset = InvoiceLineItemFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.save()
            
            # Recalculate totals
            invoice.calculate_totals()
            invoice.save()
            
            messages.success(request, f'Invoice {invoice.invoice_number} updated successfully.')
            return redirect('billing:invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceLineItemFormSet(instance=invoice)
    
    context = {
        'title': f'Edit Invoice {invoice.invoice_number}',
        'form': form,
        'formset': formset,
        'invoice': invoice,
        'submit_text': 'Update Invoice',
        'status_choices': Invoice.STATUS_CHOICES,
        'role':role
    }
    return render(request, 'billing/invoice_form.html', context)


@login_required
@permission_required('billing.delete_invoice', raise_exception=True)
def invoice_delete(request, invoice_id):
    """Delete an invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        invoice_number = invoice.invoice_number
        invoice.delete()
        messages.success(request, f'Invoice {invoice_number} deleted successfully.')
        return redirect('billing:invoice_list')
    
    context = {
        'title': f'Delete Invoice {invoice.invoice_number}',
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_delete.html', context)


@login_required
def invoice_void(request, invoice_id):
    """Void an invoice (mark as cancelled)"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Only allow voiding if invoice is not already paid or cancelled
    if invoice.status in ['paid', 'cancelled']:
        messages.error(request, f'Cannot void invoice {invoice.invoice_number}. Invoice is already {invoice.get_status_display().lower()}.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        # Get void reason from form
        void_reason = request.POST.get('void_reason', '').strip()
        
        # Update invoice status to cancelled
        invoice.status = 'cancelled'
        
        # Add void reason to notes
        void_note = f"\n\n--- INVOICE VOIDED ---\nVoided on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}\nVoided by: {request.user.get_full_name() or request.user.username}\nReason: {void_reason or 'No reason provided'}"
        invoice.notes = (invoice.notes or '') + void_note
        
        invoice.save()
        
        messages.success(request, f'Invoice {invoice.invoice_number} has been voided successfully.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'title': f'Void Invoice {invoice.invoice_number}',
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_void.html', context)


@login_required
def invoice_mark_paid(request, invoice_id):
    """Mark an invoice as paid"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Pre-populate invoice if provided via URL parameter
    initial_data = {}
    selected_invoice = None
    

    if request.method == 'POST':

        formReciept = CashChequeReceiptForm(initial=initial_data)

        if invoice.status != 'paid':
            # Get payment details from form
            payment_method = request.POST.get('payment_method', 'cash')
            reference_number = request.POST.get('reference_number', '')
            notes = request.POST.get('notes', f'Payment for invoice {invoice.invoice_number}')
            
            # Mark invoice as paid
            invoice.status = 'paid'
            invoice.save()
            
            # Create Payment record
            from payments.models import Payment
            payment = Payment.objects.create(
                invoice=invoice,
                invoice_number=invoice.invoice_number,
                amount=invoice.total_amount,
                payment_method=payment_method,
                reference_number=reference_number,
                notes=notes,
                status='completed',
                created_by=request.user
            )
            
            # Create Cash reciept
            CashChequeReceipt.objects.create(
                invoice = invoice,
                received_from = invoice.get_client_name(),
                amount_usd=invoice.total_amount,
                payment_method='cash',
                payment_purpose= f'Payment for Invoice #{invoice.invoice_number}',
                created_by=request.user
            )
            

            messages.success(request, f'Invoice {invoice.invoice_number} marked as paid. Payment record {payment.payment_number} created.')
        else:
            messages.info(request, f'Invoice {invoice.invoice_number} is already marked as paid.')
        
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'title': f'Mark Invoice as Paid',
        'invoice': invoice,
    }
    return render(request, 'billing/invoice_mark_paid.html', context)


@login_required
def invoice_pdf(request, invoice_id):
    """Generate PDF for an invoice"""
    from company.utils import get_current_company
    
    invoice = get_object_or_404(Invoice, id=invoice_id)
    line_items = invoice.line_items.all()
    
    # Get company information
    company_info = get_current_company(request)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="invoice_{invoice.invoice_number}.pdf"'
    
    # Create the PDF object using BytesIO as a file-like buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Company header
    company_style = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=10,
        alignment=1  # Center
    )
    elements.append(Paragraph(f"<b>{company_info['name']}</b>", company_style))
    elements.append(Paragraph(company_info['tagline'], styles['Normal']))
    elements.append(Paragraph(company_info['address'], styles['Normal']))
    elements.append(Paragraph(f"Phone: {company_info['phone']} | Email: {company_info['email']}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Title with watermark for cancelled invoices
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Add watermark for cancelled invoices
    if invoice.status == 'cancelled':
        # Add watermark text
        watermark_style = ParagraphStyle(
            'WatermarkStyle',
            parent=styles['Normal'],
            fontSize=48,
            textColor=colors.Color(220/255, 38/255, 38/255, alpha=0.3),
            alignment=1,
            spaceAfter=10
        )
        elements.append(Paragraph("<b>CANCELLED</b>", watermark_style))
    
    elements.append(Paragraph(f"INVOICE {invoice.invoice_number}", title_style))
    elements.append(Spacer(1, 20))
    
    # Invoice details
    details_data = [
        ['Invoice Date:', invoice.issue_date.strftime('%B %d, %Y')],
        ['Due Date:', invoice.due_date.strftime('%B %d, %Y')],
        ['Client:', invoice.get_client_name()],
        ['Status:', invoice.get_status_display()],
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 3*inch])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 30))
    
    # Line items table
    table_data = [['Description', 'Qty', 'Unit Price', 'Total']]
    for item in line_items:
        table_data.append([
            item.description,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total_amount:.2f}"
        ])
    
    # Add totals
    table_data.extend([
        ['', '', 'Subtotal:', f"${invoice.subtotal:.2f}"],
        ['', '', 'Tax:', f"${invoice.tax_amount:.2f}"],
        ['', '', 'Total:', f"${invoice.total_amount:.2f}"],
    ])
    
    items_table = Table(table_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -4), 12),
        ('ALIGN', (0, 1), (0, -4), 'LEFT'),  # Description left-aligned
        
        # Total rows
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -3), (-1, -1), 12),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        
        # Grid
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
    ]))
    elements.append(items_table)
    
    # Notes
    if invoice.notes:
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response


@login_required
def service_list(request):
    """List all services with search and filtering"""
    form = ServiceSearchForm(request.GET)
    services = Service.objects.order_by('category', 'name')
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        if search:
            services = services.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        category = form.cleaned_data.get('category')
        if category:
            services = services.filter(category=category)
        
        status = form.cleaned_data.get('status')
        if status == 'active':
            services = services.filter(is_active=True)
        elif status == 'inactive':
            services = services.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(services, 20)
    page = request.GET.get('page')
    services = paginator.get_page(page)
    
    context = {
        'title': 'Services',
        'services': services,
        'form': form,
    }
    return render(request, 'billing/service_list.html', context)


@login_required
def service_create(request):
    """Create a new service"""
    # Check if we're creating based on an existing service (for price change workaround)
    base_service_id = request.GET.get('based_on')
    base_service = None
    if base_service_id:
        try:
            base_service = Service.objects.get(id=base_service_id)
        except Service.DoesNotExist:
            base_service = None
    
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.save(user=request.user)
            
            if base_service:
                messages.success(request, f'New service "{service.name}" created successfully as a replacement for "{base_service.name}".')
            else:
                messages.success(request, f'Service "{service.name}" created successfully.')
            
            return redirect('billing:service_list')
    else:
        # Pre-populate form with base service data if provided
        if base_service:
            initial_data = {
                'name': base_service.name,
                'category': base_service.category,
                'description': base_service.description,
                'service_code': base_service.suggest_new_service_code(),
                'is_active': True,  # New service should be active
                # Don't copy default_price - let user set the new price
            }
            form = ServiceForm(initial=initial_data)
        else:
            form = ServiceForm()
    
    context = {
        'title': 'Create Service',
        'form': form,
        'submit_text': 'Create Service',
        'base_service': base_service,
    }
    return render(request, 'billing/service_form.html', context)


@login_required
def service_edit(request, service_id):
    """Edit an existing service"""
    service = get_object_or_404(Service, id=service_id)
    original_price = service.default_price
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            new_price = form.cleaned_data.get('default_price')
            
            # Check if price change is allowed
            can_change, reason = service.can_change_price(new_price)
            
            if not can_change:
                # Get usage details for better error message
                usage_info = service.is_price_used_in_calculations()
                suggested_code = service.suggest_new_service_code()
                
                # Add detailed error message with usage information
                error_message = f"Cannot change price from ${original_price} to ${new_price}. "
                error_message += f"This service is currently used in {usage_info['total_references']} transaction(s):\n\n"
                
                for detail in usage_info['usage_details']:
                    error_message += f"• {detail['type']}: {detail['count']} record(s)\n"
                    if detail['examples']:
                        error_message += f"  Examples: {', '.join(detail['examples'])}\n"
                
                error_message += f"\n💡 Solution: Create a new service with the updated price instead.\n"
                error_message += f"Suggested service code: {suggested_code}"
                
                messages.error(request, error_message)
                
                # Add context for the template to show the create new service suggestion
                context = {
                    'title': f'Edit Service: {service.name}',
                    'form': form,
                    'service': service,
                    'submit_text': 'Update Service',
                    'price_change_blocked': True,
                    'usage_info': usage_info,
                    'suggested_code': suggested_code,
                    'original_price': original_price,
                    'new_price': new_price,
                }
                return render(request, 'billing/service_form.html', context)
            
            # Price change is allowed, proceed with save
            service = form.save(commit=False)
            service.save(user=request.user)
            
            if new_price != original_price:
                messages.success(request, f'Service "{service.name}" updated successfully. Price changed from ${original_price} to ${new_price}.')
            else:
                messages.success(request, f'Service "{service.name}" updated successfully.')
            
            return redirect('billing:service_list')
    else:
        form = ServiceForm(instance=service)
    
    context = {
        'title': f'Edit Service: {service.name}',
        'form': form,
        'service': service,
        'submit_text': 'Update Service',
        'price_change_blocked': False,
    }
    return render(request, 'billing/service_form.html', context)


@login_required
def service_delete(request, service_id):
    """Delete a service - handles both modal and direct deletion"""
    
    service = get_object_or_404(Service, id=service_id)
    
    # Handle POST request (from modal or delete page)
    if request.method == 'POST':
        service_name = service.name
        
        # Get all related objects count for feedback message
        related_count = 0
        try:
            related_count += service.invoicelineitem_set.count()
        except:
            pass
        
        try:
            related_count += service.visaservicerecord_set.count()
        except:
            pass
        
        try:
            from eform.models import ExtensionRequest
            related_count += service.extensionrequest_set.count()
        except:
            pass
        
        try:
            service.delete()
            if related_count > 0:
                messages.success(
                    request, 
                    f'Service "{service_name}" and {related_count} related records deleted successfully.'
                )
            else:
                messages.success(request, f'Service "{service_name}" deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting service: {str(e)}')
        
        return redirect('billing:service_list')
    
    # For GET request, show the detailed delete page
    # Get all related objects that will be cascade deleted
    related_objects = []
    
    # Check InvoiceLineItems
    line_items = service.invoicelineitem_set.all()
    if line_items.exists():
        related_objects.append({
            'model': 'Invoice Line Items',
            'count': line_items.count(),
            'items': [f"Invoice #{item.invoice.invoice_number} - {item.description}" for item in line_items[:5]],
            'more': max(0, line_items.count() - 5)
        })
    
    # Check VisaServiceRecords
    visa_services = service.visaservicerecord_set.all()
    if visa_services.exists():
        related_objects.append({
            'model': 'Visa Service Records',
            'count': visa_services.count(),
            'items': [f"{vs.get_client_name()} - {vs.get_duration_months_display()}" for vs in visa_services[:5]],
            'more': max(0, visa_services.count() - 5)
        })
    
    # Check ExtensionRequests (from eform app)
    try:
        from eform.models import ExtensionRequest
        extension_requests = service.extensionrequest_set.all()
        if extension_requests.exists():
            related_objects.append({
                'model': 'Extension Requests',
                'count': extension_requests.count(),
                'items': [f"#{ext.request_number} - {ext.worker.get_full_name()}" for ext in extension_requests[:5]],
                'more': max(0, extension_requests.count() - 5)
            })
    except ImportError:
        pass  # eform app not available
    
    # Calculate total affected objects
    total_affected = sum(obj['count'] for obj in related_objects)
    
    context = {
        'title': f'Delete Service: {service.name}',
        'service': service,
        'related_objects': related_objects,
        'total_affected': total_affected,
        'has_dependencies': total_affected > 0,
    }
    return render(request, 'billing/service_delete.html', context)


@login_required
def service_history(request, service_id):
    """View service change history"""
    service = get_object_or_404(Service, id=service_id)
    
    # Get the change history for this service
    history_records = ServiceHistory.objects.filter(
        service=service
    ).select_related('changed_by').order_by('-changed_at')
    
    # Pagination
    paginator = Paginator(history_records, 20)
    page = request.GET.get('page')
    history_records = paginator.get_page(page)
    
    context = {
        'title': f'Change History: {service.name}',
        'service': service,
        'history_records': history_records,
    }
    return render(request, 'billing/service_history.html', context)


@login_required
def revenue_report(request):
    """Detailed revenue report"""
    # This view can be expanded with more detailed reporting
    return redirect('billing:dashboard')


@login_required
def overdue_report(request):
    """Detailed overdue invoices report"""
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(
        status='pending',
        due_date__lt=today
    ).select_related('worker').order_by('due_date')
    
    # Pagination
    paginator = Paginator(overdue_invoices, 20)
    page = request.GET.get('page')
    overdue_invoices = paginator.get_page(page)
    
    context = {
        'title': 'Overdue Invoices Report',
        'overdue_invoices': overdue_invoices,
    }
    return render(request, 'billing/overdue_report.html', context)


# AJAX endpoints
@login_required
def get_service_details(request, service_id):
    """Get service details for AJAX requests"""
    try:
        service = Service.objects.get(id=service_id)
        return JsonResponse({
            'name': service.name,
            'description': service.description,
            'default_price': str(service.default_price),
        })
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)


@login_required
def search_services(request):
    """Search services for autocomplete functionality"""
    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 10))
    
    if not query:
        return JsonResponse({'results': []})
    
    # Search in name, service_code, and description
    services = Service.objects.filter(
        is_active=True
    ).filter(
        Q(name__icontains=query) |
        Q(service_code__icontains=query) |
        Q(description__icontains=query)
    ).order_by('name')[:limit]
    
    results = []
    for service in services:
        results.append({
            'id': service.id,
            'name': service.name,
            'service_code': service.service_code or '',
            'description': service.description,
            'default_price': str(service.default_price),
            'category': service.get_category_display(),
            'display_text': f"{service.service_code} - {service.name}" if service.service_code else service.name
        })
    
    return JsonResponse({'results': results})


@login_required
def manage_line_items(request, invoice_id):
    """Manage invoice line items via AJAX"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'GET':
        line_items = invoice.line_items.all().values(
            'id', 'service__name', 'description', 'quantity', 'unit_price', 'total_amount'
        )
        return JsonResponse({'line_items': list(line_items)})
    
    # Handle POST, PUT, DELETE for line item management
    # This can be expanded based on specific AJAX requirements
    return JsonResponse({'status': 'success'})


@login_required
def ajax_search_workers(request):
    """AJAX endpoint for worker autocomplete search"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Only search when user has typed at least 2 characters
        return JsonResponse({'results': []})
    
    # Search workers by name, ID, or phone (excluding VIPs)
    # Include all worker statuses - no status filtering
    
    workers = Worker.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(worker_id__icontains=query) |
        Q(phone_number__icontains=query),
        is_vip=False  # Exclude VIP workers since they have a separate endpoint
        # Removed status filtering - allow all statuses
    ).select_related('zone', 'zone__created_by')[:10]  # Limit to 10 results for performance
    
    results = []
    for worker in workers:
        # Create display text with key information
        display_text = f"{worker.get_full_name()}"
        if worker.worker_id:
            display_text += f" (ID: {worker.worker_id})"
        if worker.zone:
            zone_name = worker.zone.name
            display_text += f" - {zone_name}"
        
        # Additional info for tooltip/subtitle
        subtitle = []
        if worker.phone_number:
            subtitle.append(f"Phone: {worker.phone_number}")
        if worker.position:
            subtitle.append(f"Position: {worker.position.name}")
        
        results.append({
            'id': worker.id,
            'text': display_text,
            'subtitle': ' | '.join(subtitle),
            'name': worker.get_full_name(),
            'worker_id': worker.worker_id or '',
            'phone': worker.phone_number or '',
            'zone': zone_name if worker.zone else ''
        })
    
    return JsonResponse({'results': results})


@login_required
def ajax_search_vips(request):
    """AJAX endpoint for VIP autocomplete search"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Only search when user has typed at least 2 characters
        return JsonResponse({'results': []})
    
    # Search for VIP workers (workers with is_vip=True)
    # Include all worker statuses - no status filtering
    
    vip_workers = Worker.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(worker_id__icontains=query) |
        Q(phone_number__icontains=query),
        is_vip=True
        # Removed status filtering - allow all statuses
    ).select_related('zone', 'zone__created_by')[:10]  # Limit to 10 results for performance
    
    results = []
    for worker in vip_workers:
        # Create display text with key information
        display_text = f"{worker.get_full_name()} [VIP]"
        if worker.worker_id:
            display_text += f" (ID: {worker.worker_id})"
        if worker.zone:
            zone_name = worker.zone.name
            display_text += f" - {zone_name}"
        
        # Additional info for tooltip/subtitle
        subtitle = []
        if worker.phone_number:
            subtitle.append(f"Phone: {worker.phone_number}")
        if worker.position:
            subtitle.append(f"Position: {worker.position.name}")
        
        results.append({
            'id': worker.id,
            'text': display_text,
            'subtitle': ' | '.join(subtitle),
            'name': worker.get_full_name(),
            'worker_id': worker.worker_id or '',
            'phone': worker.phone_number or '',
            'zone': zone_name if worker.zone else ''
        })
    
    return JsonResponse({'results': results})


@login_required
def ajax_search_batches(request):
    """AJAX endpoint for worker batch autocomplete search"""
    from zone.models import WorkerProbationPeriod
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Only search when user has typed at least 2 characters
        return JsonResponse({'results': []})
    
    # Get all unique batch names from probation periods
    probation_periods = WorkerProbationPeriod.objects.exclude(
        evaluation_notes__isnull=True
    ).exclude(
        evaluation_notes=''
    ).select_related('worker')
    
    # Extract batch names and filter by query
    batch_results = {}
    for probation in probation_periods:
        batch_name = probation.get_batch_name()
        if batch_name and query.lower() in batch_name.lower():
            if batch_name not in batch_results:
                # Count workers in this batch
                worker_count = 0
                for p in probation_periods:
                    if p.get_batch_name() == batch_name:
                        worker_count += 1
                
                batch_results[batch_name] = {
                    'name': batch_name,
                    'details': f'{worker_count} worker(s) in batch',
                    'worker_count': worker_count
                }
    
    # Sort batches by name and limit results
    sorted_batches = sorted(batch_results.values(), key=lambda x: x['name'])[:10]
    
    return JsonResponse({'results': sorted_batches})


@login_required
def batch_workers_list(request, batch_name):
    """Display list of workers in a specific batch"""
    from zone.models import WorkerProbationPeriod
    
    # Decode the batch name from URL
    import urllib.parse
    batch_name = urllib.parse.unquote(batch_name)
    
    # Get all probation periods with this batch name
    probation_periods = WorkerProbationPeriod.objects.exclude(
        evaluation_notes__isnull=True
    ).exclude(
        evaluation_notes=''
    ).select_related('worker', 'worker__zone', 'worker__position')
    
    # Filter workers by batch name
    batch_workers = []
    for probation in probation_periods:
        if probation.get_batch_name() == batch_name:
            batch_workers.append({
                'worker': probation.worker,
                'probation': probation,
                'start_date': probation.start_date,
                'end_date': probation.get_end_date(),
                'status': probation.worker.status,
                'days_remaining': probation.get_days_remaining(),
                'progress_percentage': probation.get_progress_percentage()
            })
    
    # Sort workers by name
    batch_workers.sort(key=lambda x: x['worker'].get_full_name())
    
    # Count statuses
    status_counts = {
        'probation': 0,
        'extended': 0,
        'passed': 0,
        'failed': 0,
        'terminated': 0
    }
    
    for worker_data in batch_workers:
        status = worker_data['status']
        if status in status_counts:
            status_counts[status] += 1
    
    # Check if JSON format is requested
    if request.GET.get('format') == 'json':
        try:
            # Prepare JSON response
            json_workers = []
            for worker_data in batch_workers:
                worker = worker_data['worker']
                
                # Safely get worker attributes with fallbacks
                try:
                    worker_info = {
                        'worker_name': worker.get_full_name(),
                        'worker_id': getattr(worker, 'worker_id', None),
                        'zone': worker.zone.name if getattr(worker, 'zone', None) else None,
                        'zone_code': worker.zone.code if getattr(worker, 'zone', None) else None,
                        'building': worker.building.name if getattr(worker, 'building', None) else None,
                        'building_code': worker.building.code if getattr(worker, 'building', None) else None,
                        'gender': worker.get_sex_display() if getattr(worker, 'sex', None) else None,
                        'nationality': worker.get_nationality_display() if getattr(worker, 'nationality', None) else None,
                        'status': worker_data['status'],
                        'start_date': worker_data['start_date'].strftime('%Y-%m-%d'),
                        'end_date': worker_data['end_date'].strftime('%Y-%m-%d'),
                        'days_remaining': worker_data.get('days_remaining', 0),
                        'progress_percentage': worker_data.get('progress_percentage', 0),
                        'created_date': getattr(worker, 'created_date', None)
                    }
                
                    # Handle photo safely - use photo_url property for encrypted photos
                    try:
                        if hasattr(worker, 'photo') and worker.photo:
                            worker_info['profile_photo'] = worker.photo_url
                        else:
                            worker_info['profile_photo'] = None
                    except:
                        worker_info['profile_photo'] = None
                    
                    # Handle age calculation safely
                    try:
                        if hasattr(worker, 'date_of_birth') and worker.date_of_birth:
                            from datetime import date
                            today = date.today()
                            age = today.year - worker.date_of_birth.year - ((today.month, today.day) < (worker.date_of_birth.month, worker.date_of_birth.day))
                            worker_info['age'] = age
                        else:
                            worker_info['age'] = None
                    except:
                        worker_info['age'] = None
                    
                    # Format created_date safely
                    if worker_info['created_date']:
                        try:
                            worker_info['created_date'] = worker_info['created_date'].strftime('%Y-%m-%d')
                        except:
                            worker_info['created_date'] = None
                    
                    json_workers.append(worker_info)


                except Exception as e:
                    # Log error but continue with other workers
                    # Add basic worker info as fallback
                    json_workers.append({
                        'worker_name': worker.get_full_name() if worker else 'Unknown',
                        'worker_id': getattr(worker, 'worker_id', None),
                        'phone': getattr(worker, 'phone_number', None),
                        'email': None,
                        'zone': None,
                        'position': None,
                        'nationality': None,
                        'age': None,
                        'status': worker_data.get('status', 'unknown'),
                        'start_date': worker_data['start_date'].strftime('%Y-%m-%d') if worker_data.get('start_date') else None,
                        'end_date': worker_data['end_date'].strftime('%Y-%m-%d') if worker_data.get('end_date') else None,
                        'days_remaining': 0,
                        'progress_percentage': 0,
                        'profile_photo': None,
                        'created_date': None
                    })
        
            return JsonResponse({
                'batch_name': batch_name,
                'batch_workers': json_workers,
                'worker_count': len(batch_workers),
                'status_counts': status_counts,
                'active_count': status_counts['probation'] + status_counts['extended'],
                'completed_count': status_counts['passed'],
                'terminated_count': status_counts['failed'] + status_counts['terminated']
            })
        except Exception as e:
            return JsonResponse({
                'error': f'Failed to load batch workers: {str(e)}',
                'batch_name': batch_name,
                'batch_workers': [],
                'worker_count': 0
            })
    
    # Regular HTML response
    context = {
        'batch_name': batch_name,
        'batch_workers': batch_workers,
        'worker_count': len(batch_workers),
        'status_counts': status_counts,
        'active_count': status_counts['probation'] + status_counts['extended'],
        'completed_count': status_counts['passed'],
        'terminated_count': status_counts['failed'] + status_counts['terminated'],
        'title': f'Batch Workers - {batch_name}'
    }
    
    return render(request, 'billing/batch_workers_list.html', context)


# Enhanced dashboard with receipt data
@login_required
def enhanced_billing_dashboard(request):
    """Enhanced billing dashboard including receipt metrics"""
    from .models import OfficialReceipt, CashChequeReceipt, PaymentVoucher
    
    # Calculate dashboard metrics
    today = timezone.now().date()
    this_month = today.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    
    # Revenue metrics
    total_revenue = Invoice.objects.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_revenue = Invoice.objects.filter(
        status='paid', 
        issue_date__gte=this_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Outstanding metrics
    pending_amount = Invoice.objects.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    overdue_count = Invoice.objects.filter(
        status='pending',
        due_date__lt=today
    ).count()
    
    # Receipt metrics
    total_receipts = OfficialReceipt.objects.count() + CashChequeReceipt.objects.count()
    total_vouchers = PaymentVoucher.objects.count()
    
    # Recent invoices and receipts
    recent_invoices = Invoice.objects.select_related('worker').order_by('-created_at')[:5]
    recent_receipts = OfficialReceipt.objects.order_by('-created_at')[:5]
    
    # Monthly comparison
    last_month_revenue = Invoice.objects.filter(
        status='paid',
        issue_date__gte=last_month,
        issue_date__lt=this_month
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    revenue_change = 0
    if last_month_revenue > 0:
        revenue_change = ((monthly_revenue - last_month_revenue) / last_month_revenue) * 100
    
    context = {
        'title': 'Billing Dashboard',
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'pending_amount': pending_amount,
        'overdue_count': overdue_count,
        'total_receipts': total_receipts,
        'total_vouchers': total_vouchers,
        'recent_invoices': recent_invoices,
        'recent_receipts': recent_receipts,
        'revenue_change': revenue_change,
        'revenue_trend': 'up' if revenue_change > 0 else 'down' if revenue_change < 0 else 'same',
    }
    return render(request, 'billing/dashboard.html', context)


# Official Receipt Views
@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def official_receipt_list(request):
    """List all official receipts"""
    from .models import OfficialReceipt
    
    receipts = OfficialReceipt.objects.order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        receipts = receipts.filter(
            Q(receipt_number__icontains=search) |
            Q(employee_name__icontains=search) |
            Q(employee_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(receipts, 20)
    page = request.GET.get('page')
    receipts = paginator.get_page(page)
    
    context = {
        'title': 'Official Receipts',
        'receipts': receipts,
        'search': search,
    }
    return render(request, 'billing/official_receipt_list.html', context)


@login_required
@permission_required('billing.add_invoice', raise_exception=True)
def official_receipt_create(request):
    """Create new official receipt"""
    from .models import OfficialReceipt
    from .forms import OfficialReceiptForm
    
    # Pre-populate invoice if provided via URL parameter
    initial_data = {}
    invoice_id = request.GET.get('invoice')
    selected_invoice = None
    
    if invoice_id:
        try:
            selected_invoice = Invoice.objects.get(id=invoice_id)
            initial_data['invoice'] = selected_invoice
            # Pre-populate some fields from invoice
            initial_data['employee_name'] = selected_invoice.get_client_name()
            initial_data['total_amount'] = selected_invoice.total_amount
        except Invoice.DoesNotExist:
            messages.warning(request, 'Selected invoice not found.')
    
    if request.method == 'POST':
        form = OfficialReceiptForm(request.POST, initial=initial_data)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.created_by = request.user
            
            # Handle invoice connection from hidden field or form
            invoice_id_from_form = request.POST.get('invoice_id')
            if invoice_id_from_form:
                try:
                    receipt.invoice = Invoice.objects.get(id=invoice_id_from_form)
                except Invoice.DoesNotExist:
                    pass
            
            receipt.save()
            
            # If connected to an invoice, mark the invoice as paid
            if receipt.invoice and receipt.invoice.status == 'pending':
                receipt.invoice.status = 'paid'
                receipt.invoice.save()
                messages.success(request, f'Official Receipt {receipt.receipt_number} created and Invoice #{receipt.invoice.invoice_number} marked as paid.')
            else:
                messages.success(request, f'Official Receipt {receipt.receipt_number} created successfully.')
                
            return redirect('billing:official_receipt_detail', receipt_id=receipt.id)
    else:
        form = OfficialReceiptForm(initial=initial_data)
    
    context = {
        'title': 'Create Official Receipt',
        'form': form,
        'selected_invoice': selected_invoice,
        'current_year': timezone.now().year,
        'submit_text': 'Create Receipt',
    }
    return render(request, 'billing/official_receipt_form.html', context)


@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def official_receipt_detail(request, receipt_id):
    """View official receipt details"""
    from .models import OfficialReceipt
    
    receipt = get_object_or_404(OfficialReceipt, id=receipt_id)
    
    context = {
        'title': f'Official Receipt {receipt.receipt_number}',
        'receipt': receipt,
    }
    return render(request, 'billing/official_receipt_detail.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def official_receipt_edit(request, receipt_id):
    """Edit official receipt"""
    from .models import OfficialReceipt
    
    receipt = get_object_or_404(OfficialReceipt, id=receipt_id)
    
    if request.method == 'POST':
        receipt.receipt_type = request.POST.get('receipt_type', receipt.receipt_type)
        receipt.employee_number = request.POST.get('employee_number', receipt.employee_number)
        receipt.employee_name = request.POST.get('employee_name', receipt.employee_name)
        receipt.total_pass = int(request.POST.get('total_pass', receipt.total_pass))
        receipt.total_amount = float(request.POST.get('total_amount', receipt.total_amount))
        receipt.service_fee_5 = float(request.POST.get('service_fee_5', receipt.service_fee_5))
        receipt.quota_fee_25 = float(request.POST.get('quota_fee_25', receipt.quota_fee_25))
        receipt.support_document_amount = float(request.POST.get('support_document_amount', receipt.support_document_amount))
        receipt.year = int(request.POST.get('year', receipt.year))
        receipt.notes = request.POST.get('notes', receipt.notes)
        receipt.save()
        
        messages.success(request, f'Official Receipt {receipt.receipt_number} updated successfully.')
        return redirect('billing:official_receipt_detail', receipt_id=receipt.id)
    
    context = {
        'title': f'Edit Official Receipt {receipt.receipt_number}',
        'receipt': receipt,
    }
    return render(request, 'billing/official_receipt_form.html', context)


@login_required
@permission_required('billing.delete_invoice', raise_exception=True)
def official_receipt_delete(request, receipt_id):
    """Delete official receipt"""
    from .models import OfficialReceipt
    
    receipt = get_object_or_404(OfficialReceipt, id=receipt_id)
    
    if request.method == 'POST':
        receipt_number = receipt.receipt_number
        receipt.delete()
        messages.success(request, f'Official Receipt {receipt_number} deleted successfully.')
        return redirect('billing:official_receipt_list')
    
    context = {
        'title': f'Delete Official Receipt {receipt.receipt_number}',
        'receipt': receipt,
    }
    return render(request, 'billing/confirm_delete.html', context)


@login_required
def official_receipt_print(request, receipt_id):
    """Print official receipt"""
    from .models import OfficialReceipt
    
    receipt = get_object_or_404(OfficialReceipt, id=receipt_id)
    
    context = {
        'receipt': receipt,
    }
    return render(request, 'billing/official_receipt_print.html', context)


# Cash Receipt Views
@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def cash_receipt_list(request):
    """List all cash receipts"""
    from .models import CashChequeReceipt
    
    if request.GET.get('invoice'):
        receipts = CashChequeReceipt.objects.filter(invoice=request.GET.get('invoice')).order_by('-created_at')
    else:
        receipts = CashChequeReceipt.objects.order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        receipts = receipts.filter(
            Q(receipt_number__icontains=search) |
            Q(received_from__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(receipts, 20)
    page = request.GET.get('page')
    receipts = paginator.get_page(page)
    
    context = {
        'title': 'Cash/Cheque Receipts',
        'receipts': receipts,
        'search': search,
    }
    return render(request, 'billing/cash_receipt_list.html', context)


@login_required
@permission_required('billing.add_invoice', raise_exception=True)
def cash_receipt_create(request):
    """Create new cash/cheque receipt"""
    from .models import CashChequeReceipt
    from .forms import CashChequeReceiptForm
    
    # Pre-populate invoice if provided via URL parameter
    initial_data = {}
    invoice_id = request.GET.get('invoice')
    selected_invoice = None
    
    if invoice_id:
        try:
            selected_invoice = Invoice.objects.get(id=invoice_id)
            initial_data['invoice'] = selected_invoice
            # Pre-populate some fields from invoice
            initial_data['received_from'] = selected_invoice.get_client_name()
            initial_data['amount_usd'] = selected_invoice.total_amount
            initial_data['payment_purpose'] = f'Payment for Invoice #{selected_invoice.invoice_number}'
        except Invoice.DoesNotExist:
            messages.warning(request, 'Selected invoice not found.')
    
    if request.method == 'POST':
        form = CashChequeReceiptForm(request.POST, initial=initial_data)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.created_by = request.user
            
            # Handle invoice connection from hidden field or form
            invoice_id_from_form = request.POST.get('invoice_id')
            if invoice_id_from_form:
                try:
                    receipt.invoice = Invoice.objects.get(id=invoice_id_from_form)
                except Invoice.DoesNotExist:
                    pass
            
            receipt.save()
            
            # If connected to an invoice, mark the invoice as paid
            if receipt.invoice and receipt.invoice.status == 'pending':
                receipt.invoice.status = 'paid'
                receipt.invoice.save()
                messages.success(request, f'Cash Receipt {receipt.receipt_number} created and Invoice #{receipt.invoice.invoice_number} marked as paid.')
            else:
                messages.success(request, f'Cash Receipt {receipt.receipt_number} created successfully.')
                
            return redirect('billing:cash_receipt_detail', receipt_id=receipt.id)
    else:
        form = CashChequeReceiptForm(initial=initial_data)
    
    context = {
        'title': 'Record Payment - Cash/Cheque Receipt',
        'form': form,
        'selected_invoice': selected_invoice,
        'submit_text': 'Record Payment',
    }
    return render(request, 'billing/cash_receipt_form.html', context)


@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def cash_receipt_detail(request, receipt_id):
    """View cash receipt details"""
    from .models import CashChequeReceipt
    
    receipt = get_object_or_404(CashChequeReceipt, id=receipt_id)
    
    context = {
        'title': f'Cash Receipt {receipt.receipt_number}',
        'receipt': receipt,
    }
    return render(request, 'billing/cash_receipt_detail.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def cash_receipt_edit(request, receipt_id):
    """Edit cash receipt"""
    from .models import CashChequeReceipt
    from .forms import CashChequeReceiptForm
    
    receipt = get_object_or_404(CashChequeReceipt, id=receipt_id)
    
    if request.method == 'POST':
        form = CashChequeReceiptForm(request.POST, instance=receipt)
        if form.is_valid():
            form.save()
            messages.success(request, f'Cash Receipt {receipt.receipt_number} updated successfully.')
            return redirect('billing:cash_receipt_detail', receipt_id=receipt.id)
    else:
        form = CashChequeReceiptForm(instance=receipt)
    
    context = {
        'title': f'Edit Cash Receipt {receipt.receipt_number}',
        'receipt': receipt,
        'form': form,
        'submit_text': 'Update Receipt',
    }
    return render(request, 'billing/cash_receipt_form.html', context)


@login_required
@permission_required('billing.delete_invoice', raise_exception=True)
def cash_receipt_delete(request, receipt_id):
    """Delete cash receipt"""
    from .models import CashChequeReceipt
    
    receipt = get_object_or_404(CashChequeReceipt, id=receipt_id)
    
    if request.method == 'POST':
        receipt_number = receipt.receipt_number
        receipt.delete()
        messages.success(request, f'Cash Receipt {receipt_number} deleted successfully.')
        return redirect('billing:cash_receipt_list')
    
    context = {
        'title': f'Delete Cash Receipt {receipt.receipt_number}',
        'receipt': receipt,
    }
    return render(request, 'billing/confirm_delete.html', context)


@login_required
def cash_receipt_print(request, receipt_id):
    """Print cash receipt"""
    from .models import CashChequeReceipt
    from company.utils import get_company_context

    receipt = get_object_or_404(CashChequeReceipt, id=receipt_id)
    
    context = {
        'receipt': receipt,
    }
    context.update(get_company_context(request))
    
    return render(request, 'billing/cash_receipt_print.html', context)


# Payment Voucher Views
@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def payment_voucher_list(request):
    """List all payment vouchers with dashboard statistics"""
    from .models import PaymentVoucher
    
    try:
        all_vouchers = PaymentVoucher.objects.all()
        vouchers = PaymentVoucher.objects.order_by('-created_at')
    except Exception as e:
        # If table doesn't exist, return empty queryset
        all_vouchers = PaymentVoucher.objects.none()
        vouchers = PaymentVoucher.objects.none()
    
    # Apply filters
    search = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    has_invoice = request.GET.get('has_invoice')
    
    if search:
        vouchers = vouchers.filter(
            Q(voucher_number__icontains=search) |
            Q(payee__icontains=search) |
            Q(payment_purpose__icontains=search)
        )
    
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__gte=date_from_parsed)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
            vouchers = vouchers.filter(date__lte=date_to_parsed)
        except ValueError:
            pass
    
    if has_invoice == 'yes':
        vouchers = vouchers.filter(invoice__isnull=False)
    elif has_invoice == 'no':
        vouchers = vouchers.filter(invoice__isnull=True)
    
    # Calculate dashboard statistics based on ALL vouchers (not filtered)
    try:
        total_amount = all_vouchers.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
        
        # This month count
        today = timezone.now().date()
        this_month_start = today.replace(day=1)
        this_month_count = all_vouchers.filter(date__gte=this_month_start).count()
        
        # Connected to invoices count
        connected_count = all_vouchers.filter(invoice__isnull=False).count()
        
    except Exception as e:

        
        pass
        # Handle cases where PaymentVoucher table is not accessible
        total_amount = 0
        this_month_count = 0
        connected_count = 0
    
    # Pagination
    paginator = Paginator(vouchers, 20)
    page = request.GET.get('page')
    vouchers_page = paginator.get_page(page)
    
    context = {
        'title': 'Payment Vouchers',
        'vouchers': vouchers_page,
        'total_amount': total_amount,
        'this_month_count': this_month_count,
        'connected_count': connected_count,
        'search': search,
        'is_paginated': vouchers_page.has_other_pages,
        'page_obj': vouchers_page,
        'paginator': paginator,
    }
    return render(request, 'billing/payment_voucher_list.html', context)


@login_required
@permission_required('billing.add_invoice', raise_exception=True)
def payment_voucher_create(request):
    """Create new payment voucher with document uploads"""
    from .models import PaymentVoucher
    from .forms import PaymentVoucherForm, PaymentVoucherDocumentFormSet
    
    # Pre-populate invoice if provided via URL parameter
    initial_data = {}
    invoice_id = request.GET.get('invoice')
    if invoice_id:
        try:
            invoice = Invoice.objects.get(id=invoice_id, status='pending')
            initial_data['invoice'] = invoice
        except Invoice.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = PaymentVoucherForm(request.POST, initial=initial_data)
        formset = PaymentVoucherDocumentFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            voucher = form.save(commit=False)
            voucher.created_by = request.user
            voucher.save()
            
            # Save the document formset
            formset.instance = voucher
            documents = formset.save(commit=False)
            for doc in documents:
                doc.payment_voucher = voucher
                doc.uploaded_by = request.user
                doc.save()
            formset.save_m2m()
            
            messages.success(request, f'Payment Voucher {voucher.voucher_number} created successfully.')
            return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    else:
        form = PaymentVoucherForm(initial=initial_data)
        formset = PaymentVoucherDocumentFormSet()
    
    context = {
        'title': 'Create Payment Voucher',
        'form': form,
        'document_formset': formset,
        'submit_text': 'Create Payment Voucher',
    }
    return render(request, 'billing/payment_voucher_form.html', context)


@login_required
@permission_required('billing.view_invoice', raise_exception=True)
def payment_voucher_detail(request, voucher_id):
    """View payment voucher details"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Calculate role-based permissions for template
    can_approve = voucher.can_approve(request.user)
    can_reject = voucher.can_reject(request.user)
    can_submit = voucher.can_submit_for_approval() and voucher.created_by == request.user
    
    context = {
        'title': f'Payment Voucher {voucher.voucher_number}',
        'voucher': voucher,
        'can_approve': can_approve,
        'can_reject': can_reject,
        'can_submit': can_submit,
    }
    return render(request, 'billing/payment_voucher_detail.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def payment_voucher_edit(request, voucher_id):
    """Edit payment voucher with document uploads"""
    from .models import PaymentVoucher
    from .forms import PaymentVoucherForm, PaymentVoucherDocumentFormSet
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Only allow editing if voucher is in draft or rejected status
    if voucher.status not in ['draft', 'rejected']:
        messages.error(request, 'Payment voucher cannot be edited in its current status.')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    if request.method == 'POST':
        form = PaymentVoucherForm(request.POST, instance=voucher)
        formset = PaymentVoucherDocumentFormSet(request.POST, request.FILES, instance=voucher)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            
            # Save the document formset
            documents = formset.save(commit=False)
            for doc in documents:
                doc.uploaded_by = request.user
                doc.save()
            # Handle deletions
            for doc in formset.deleted_objects:
                doc.delete()
            
            messages.success(request, f'Payment Voucher {voucher.voucher_number} updated successfully.')
            return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    else:
        form = PaymentVoucherForm(instance=voucher)
        formset = PaymentVoucherDocumentFormSet(instance=voucher)
    
    context = {
        'title': f'Edit Payment Voucher {voucher.voucher_number}',
        'voucher': voucher,
        'form': form,
        'document_formset': formset,
        'submit_text': 'Update Payment Voucher',
    }
    return render(request, 'billing/payment_voucher_form.html', context)


@login_required
@permission_required('billing.delete_invoice', raise_exception=True)
def payment_voucher_delete(request, voucher_id):
    """Delete payment voucher"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    if request.method == 'POST':
        voucher_number = voucher.voucher_number
        voucher.delete()
        messages.success(request, f'Payment Voucher {voucher_number} deleted successfully.')
        return redirect('billing:payment_voucher_list')
    
    # For GET requests, redirect to detail page since we use modal for deletion
    return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)


@login_required
def payment_voucher_print(request, voucher_id):
    """Print payment voucher"""
    from .models import PaymentVoucher
    from company.utils import get_company_context
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    context = {
        'voucher': voucher,
    }
    context.update(get_company_context(request))
    return render(request, 'billing/payment_voucher_print.html', context)


@login_required
def receipt_summary_report(request):
    """Receipt summary report"""
    from .models import OfficialReceipt, CashChequeReceipt, PaymentVoucher
    
    # Get summary statistics
    try:
        official_receipts_count = OfficialReceipt.objects.count()
        official_total = OfficialReceipt.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    except:
        official_receipts_count = 0
        official_total = 0
    
    try:
        cash_receipts_count = CashChequeReceipt.objects.count()
        cash_total = CashChequeReceipt.objects.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
    except:
        cash_receipts_count = 0
        cash_total = 0
        
    try:
        payment_vouchers_count = PaymentVoucher.objects.count()
        voucher_total = PaymentVoucher.objects.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
    except:
        payment_vouchers_count = 0
        voucher_total = 0
    
    context = {
        'title': 'Receipt Summary Report',
        'official_receipts_count': official_receipts_count,
        'cash_receipts_count': cash_receipts_count,
        'payment_vouchers_count': payment_vouchers_count,
        'official_total': official_total,
        'cash_total': cash_total,
        'voucher_total': voucher_total,
        'grand_total': official_total + cash_total + voucher_total,
    }
    return render(request, 'billing/receipt_summary_report.html', context)


@login_required
def visa_services_dashboard(request):
    """Visa services dashboard with key metrics and reports"""
    from .models import VisaServiceRecord
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Key metrics
    total_visa_revenue = VisaServiceRecord.objects.filter(status='paid').aggregate(
        Sum('amount'))['amount__sum'] or 0
    
    monthly_visa_revenue = VisaServiceRecord.objects.filter(
        status='paid', 
        payment_date__gte=this_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    pending_payments = VisaServiceRecord.objects.filter(status='pending').count()
    expiring_soon = VisaServiceRecord.objects.filter(
        status='paid',
        end_date__lte=today + timedelta(days=30),
        end_date__gt=today
    ).count()
    
    # Active services by duration
    duration_stats = VisaServiceRecord.objects.filter(
        status='paid',
        end_date__gt=today
    ).values('duration_months').annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('-duration_months')
    
    # Recent visa services
    recent_services = VisaServiceRecord.objects.select_related(
        'worker', 'service'
    ).order_by('-created_at')[:10]
    
    # Expiring services
    expiring_services = VisaServiceRecord.objects.filter(
        status='paid',
        end_date__lte=today + timedelta(days=30),
        end_date__gt=today
    ).select_related('worker', 'service').order_by('end_date')[:5]
    
    context = {
        'title': 'Visa Services Dashboard',
        'total_visa_revenue': total_visa_revenue,
        'monthly_visa_revenue': monthly_visa_revenue,
        'pending_payments': pending_payments,
        'expiring_soon': expiring_soon,
        'duration_stats': duration_stats,
        'recent_services': recent_services,
        'expiring_services': expiring_services,
    }
    return render(request, 'billing/visa_services_dashboard.html', context)


@login_required
def visa_service_create(request):
    """Create a new visa service record"""
    from .models import VisaServiceRecord
    from .forms import VisaServiceRecordForm
    
    if request.method == 'POST':
        form = VisaServiceRecordForm(request.POST)
        if form.is_valid():
            visa_service = form.save(commit=False)
            visa_service.created_by = request.user
            visa_service.save()
            
            # Create invoice if requested
            if request.POST.get('create_invoice'):
                invoice = Invoice.objects.create(
                    created_by=request.user,
                    worker=visa_service.worker,
                    client_name=visa_service.client_name,
                    issue_date=visa_service.start_date,
                    due_date=visa_service.start_date + timedelta(days=30),
                    status='pending'
                )
                
                # Add line item
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    service=visa_service.service,
                    description=f"{visa_service.service.name} ({visa_service.get_duration_months_display()})",
                    quantity=1,
                    unit_price=visa_service.amount,
                    total_amount=visa_service.amount
                )
                
                invoice.calculate_totals()
                invoice.save()
                
                visa_service.invoice = invoice
                visa_service.save()
                
                messages.success(request, f'Visa service created and invoice {invoice.invoice_number} generated.')
            else:
                messages.success(request, 'Visa service record created successfully.')
            
            return redirect('billing:visa_service_detail', service_id=visa_service.id)
    else:
        form = VisaServiceRecordForm()
    
    context = {
        'title': 'Create Visa Service',
        'form': form,
        'submit_text': 'Create Service',
    }
    return render(request, 'billing/visa_service_form.html', context)


@login_required
def visa_service_list(request):
    """List all visa service records with filtering"""
    from .models import VisaServiceRecord
    
    services = VisaServiceRecord.objects.select_related(
        'worker', 'service', 'invoice'
    ).order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status', '')
    duration_filter = request.GET.get('duration', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        services = services.filter(status=status_filter)
    
    if duration_filter:
        services = services.filter(duration_months=duration_filter)
    
    if search:
        services = services.filter(
            Q(worker__first_name__icontains=search) |
            Q(worker__last_name__icontains=search) |
            Q(client_name__icontains=search) |
            Q(service__name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(services, 20)
    page = request.GET.get('page')
    services = paginator.get_page(page)
    
    context = {
        'title': 'Visa Services',
        'services': services,
        'status_filter': status_filter,
        'duration_filter': duration_filter,
        'search': search,
        'status_choices': VisaServiceRecord.STATUS_CHOICES,
        'duration_choices': VisaServiceRecord.DURATION_CHOICES,
    }
    return render(request, 'billing/visa_service_list.html', context)


@login_required
def visa_service_detail(request, service_id):
    """View visa service details"""
    from .models import VisaServiceRecord
    
    service = get_object_or_404(VisaServiceRecord, id=service_id)
    
    context = {
        'title': f'Visa Service - {service.get_client_name()}',
        'service': service,
    }
    return render(request, 'billing/visa_service_detail.html', context)


@login_required 
def visa_services_report(request):
    """Generate visa services revenue report"""
    from .models import VisaServiceRecord
    from django.utils import timezone
    from datetime import timedelta
    
    # Date range filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    duration_filter = request.GET.get('duration', '')
    status_filter = request.GET.get('status', '')
    
    today = timezone.now().date()
    
    # Default date range (last 3 months)
    if not date_from:
        date_from = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = today.strftime('%Y-%m-%d')
    
    services = VisaServiceRecord.objects.filter(
        created_at__date__gte=date_from,
        created_at__date__lte=date_to
    )
    
    if duration_filter:
        services = services.filter(duration_months=duration_filter)
    
    if status_filter:
        services = services.filter(status=status_filter)
    
    # Calculate summary statistics
    total_services = services.count()
    total_revenue = services.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_revenue = services.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Revenue by duration
    revenue_by_duration = services.filter(status='paid').values(
        'duration_months'
    ).annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('-duration_months')
    
    # Monthly breakdown
    monthly_breakdown = services.filter(status='paid').extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('amount')
    ).order_by('month')
    
    context = {
        'title': 'Visa Services Report',
        'services': services.select_related('worker', 'service')[:50],
        'date_from': date_from,
        'date_to': date_to,
        'duration_filter': duration_filter,
        'status_filter': status_filter,
        'total_services': total_services,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'revenue_by_duration': revenue_by_duration,
        'monthly_breakdown': monthly_breakdown,
        'duration_choices': VisaServiceRecord.DURATION_CHOICES,
        'status_choices': VisaServiceRecord.STATUS_CHOICES,
    }
    return render(request, 'billing/visa_services_report.html', context)



# Modern Print Preview Views
@login_required
def invoice_print_preview(request, invoice_id):
    """Modern invoice print preview"""
    from company.utils import get_company_context
    
    invoice = get_object_or_404(Invoice, id=invoice_id)
    line_items = invoice.line_items.all()
    
    # Get company information from current tenant
    context = {
        'invoice': invoice,
        'line_items': line_items,
    }
    
    # Add company context
    context.update(get_company_context(request))
    
    return render(request, 'prints/invoice_print.html', context)


@login_required
def payment_voucher_print_preview(request, voucher_id):
    """Modern payment voucher print preview"""
    from company.utils import get_company_context
    
    try:
        from .models import PaymentVoucher
        voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
        
        context = {
            'voucher': voucher,
        }
        
        # Add company context
        context.update(get_company_context(request))
        
        return render(request, 'billing/payment_voucher_print.html', context)
    except ImportError:
        messages.error(request, 'Payment voucher model not available.')
        return redirect('billing:dashboard')


# Payment Voucher Workflow Views
@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def payment_voucher_submit(request, voucher_id):
    """Submit payment voucher for approval"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Check if user can submit
    if not voucher.can_submit_for_approval:
        messages.error(request, f'Payment voucher cannot be submitted. Current status: {voucher.get_status_display()}')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    # Check if user is the creator or has permission
    if voucher.created_by != request.user and not request.user.has_perm('billing.add_invoice'):
        messages.error(request, 'You can only submit payment vouchers that you created.')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    if request.method == 'POST':
        try:
            voucher.submit_for_approval(request.user)
            messages.success(request, f'Payment voucher {voucher.voucher_number} has been submitted for approval.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    context = {
        'title': f'Submit Payment Voucher {voucher.voucher_number}',
        'voucher': voucher,
        'action': 'submit',
    }
    return render(request, 'billing/payment_voucher_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def payment_voucher_approve(request, voucher_id):
    """Approve payment voucher"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Check if voucher can be approved with role-based permissions
    if not voucher.can_approve(request.user):
        messages.error(request, f'You do not have permission to approve this payment voucher. Managers can only approve vouchers created by other users.')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    if request.method == 'POST':
        try:
            voucher.approve_voucher(request.user)
            messages.success(request, f'Payment voucher {voucher.voucher_number} has been approved.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    context = {
        'title': f'Approve Payment Voucher {voucher.voucher_number}',
        'voucher': voucher,
        'action': 'approve',
    }
    return render(request, 'billing/payment_voucher_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def payment_voucher_reject(request, voucher_id):
    """Reject payment voucher"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Check if voucher can be rejected with role-based permissions
    if not voucher.can_reject(request.user):
        messages.error(request, f'You do not have permission to reject this payment voucher. Managers can only reject vouchers created by other users.')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        
        if not rejection_reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return render(request, 'billing/payment_voucher_workflow_action.html', {
                'title': f'Reject Payment Voucher {voucher.voucher_number}',
                'voucher': voucher,
                'action': 'reject',
            })
        
        try:
            voucher.reject_voucher(request.user, rejection_reason)
            messages.success(request, f'Payment voucher {voucher.voucher_number} has been rejected.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    context = {
        'title': f'Reject Payment Voucher {voucher.voucher_number}',
        'voucher': voucher,
        'action': 'reject',
    }
    return render(request, 'billing/payment_voucher_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def payment_voucher_mark_paid(request, voucher_id):
    """Mark payment voucher as paid"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Check if voucher can be marked as paid
    if not voucher.can_mark_paid:
        messages.error(request, f'Payment voucher cannot be marked as paid. Current status: {voucher.get_status_display()}')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    if request.method == 'POST':
        # Update payment details
        payment_reference = request.POST.get('payment_reference', '').strip()
        payment_notes = request.POST.get('payment_notes', '').strip()
        
        if payment_reference:
            voucher.payment_reference = payment_reference
        
        if payment_notes:
            if voucher.notes:
                voucher.notes += f"\n\nPayment Notes: {payment_notes}"
            else:
                voucher.notes = f"Payment Notes: {payment_notes}"
        
        try:
            voucher.mark_paid(request.user)
            messages.success(request, f'Payment voucher {voucher.voucher_number} has been marked as paid.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    context = {
        'title': f'Mark Payment Voucher {voucher.voucher_number} as Paid',
        'voucher': voucher,
        'action': 'mark_paid',
    }
    return render(request, 'billing/payment_voucher_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def payment_voucher_cancel(request, voucher_id):
    """Cancel payment voucher"""
    from .models import PaymentVoucher
    
    voucher = get_object_or_404(PaymentVoucher, id=voucher_id)
    
    # Check if voucher can be cancelled
    if voucher.status == 'paid':
        messages.error(request, 'Cannot cancel a paid payment voucher.')
        return redirect('billing:payment_voucher_detail', voucher_id=voucher.id)
    
    if request.method == 'POST':
        try:
            voucher.cancel_voucher(request.user)
            messages.success(request, f'Payment voucher {voucher.voucher_number} has been cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:payment_voucher_list')
    
    context = {
        'title': f'Cancel Payment Voucher {voucher.voucher_number}',
        'voucher': voucher,
        'action': 'cancel',
    }
    return render(request, 'billing/payment_voucher_workflow_action.html', context)


@login_required
def receipt_print_preview(request, receipt_id):
    """Modern receipt print preview"""
    from company.utils import get_company_context
    
    try:
        from .models import CashChequeReceipt
        receipt = get_object_or_404(CashChequeReceipt, id=receipt_id)
        
        context = {
            'receipt': receipt,
        }
        
        # Add company context
        context.update(get_company_context(request))
        
        return render(request, 'prints/receipt_voucher_print.html', context)
    except ImportError:
        messages.error(request, 'Receipt model not available.')
        return redirect('billing:dashboard')


# Invoice Workflow Views
@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def invoice_submit(request, invoice_id):
    """Submit invoice for approval"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check if user can submit
    if not invoice.can_submit_for_approval():
        messages.error(request, f'Invoice cannot be submitted. Current status: {invoice.get_status_display()}')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    # Check if user is the creator or has permission
    if invoice.created_by != request.user and not request.user.has_perm('billing.add_invoice'):
        messages.error(request, 'You can only submit invoices that you created.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        try:
            invoice.submit_for_approval(request.user)
            messages.success(request, f'Invoice {invoice.invoice_number} has been submitted for approval.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'title': f'Submit Invoice {invoice.invoice_number}',
        'invoice': invoice,
        'action': 'submit',
    }
    return render(request, 'billing/invoice_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def invoice_approve(request, invoice_id):
    """Approve invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check if invoice can be approved with role-based permissions
    if not invoice.can_approve(request.user):
        messages.error(request, f'You do not have permission to approve this invoice. Only managers can approve invoices.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        try:
            invoice.approve_invoice(request.user)
            messages.success(request, f'Invoice {invoice.invoice_number} has been approved.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'title': f'Approve Invoice {invoice.invoice_number}',
        'invoice': invoice,
        'action': 'approve',
    }
    return render(request, 'billing/invoice_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def invoice_reject(request, invoice_id):
    """Reject invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check if invoice can be rejected with role-based permissions
    if not invoice.can_reject(request.user):
        messages.error(request, f'You do not have permission to reject this invoice. Only managers can reject invoices.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        
        if not rejection_reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return render(request, 'billing/invoice_workflow_action.html', {
                'title': f'Reject Invoice {invoice.invoice_number}',
                'invoice': invoice,
                'action': 'reject',
            })
        
        try:
            invoice.reject_invoice(request.user, rejection_reason)
            messages.success(request, f'Invoice {invoice.invoice_number} has been rejected.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'title': f'Reject Invoice {invoice.invoice_number}',
        'invoice': invoice,
        'action': 'reject',
    }
    return render(request, 'billing/invoice_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def invoice_send_to_client(request, invoice_id):
    """Send approved invoice to client for payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check if invoice can be sent to client
    if invoice.status != 'approved':
        messages.error(request, f'Invoice cannot be sent to client. Current status: {invoice.get_status_display()}')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        try:
            invoice.send_to_client(request.user)
            messages.success(request, f'Invoice {invoice.invoice_number} has been sent to client and is now pending payment.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    context = {
        'title': f'Send Invoice {invoice.invoice_number} to Client',
        'invoice': invoice,
        'action': 'send_to_client',
    }
    return render(request, 'billing/invoice_workflow_action.html', context)


@login_required
@permission_required('billing.change_invoice', raise_exception=True)
def invoice_cancel(request, invoice_id):
    """Cancel invoice"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check if invoice can be cancelled
    if invoice.status == 'paid':
        messages.error(request, 'Cannot cancel a paid invoice.')
        return redirect('billing:invoice_detail', invoice_id=invoice.id)
    
    if request.method == 'POST':
        try:
            invoice.cancel_invoice(request.user)
            messages.success(request, f'Invoice {invoice.invoice_number} has been cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('billing:invoice_list')
    
    context = {
        'title': f'Cancel Invoice {invoice.invoice_number}',
        'invoice': invoice,
        'action': 'cancel',
    }
    return render(request, 'billing/invoice_workflow_action.html', context)