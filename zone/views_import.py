"""
Views for worker import functionality
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponse, Http404
from django.db import transaction
from .forms import WorkerExcelImportForm
try:
    from .forms_test import SimpleExcelImportForm
except ImportError:
    SimpleExcelImportForm = WorkerExcelImportForm
from .worker_import import ExcelWorkerImporter
import tempfile
import os
import logging

logger = logging.getLogger(__name__)


@login_required
@permission_required('zone.add_worker', raise_exception=True)
@csrf_protect
def import_workers_view(request):
    """Main view for importing workers from Excel"""
    
    if request.method == 'POST':
        
        # Use simple form for testing if requested
        FormClass = SimpleExcelImportForm if request.GET.get('test') else WorkerExcelImportForm
        form = FormClass(request.POST, request.FILES)
        
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            update_existing = form.cleaned_data['update_existing']
            skip_duplicates = form.cleaned_data['skip_duplicates']
            
            # Save uploaded file temporarily
            temp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                    temp_path = tmp_file.name
                    for chunk in excel_file.chunks():
                        tmp_file.write(chunk)
                    tmp_file.flush()
                
                # Validate that the file is a proper Excel file
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(temp_path, read_only=True)
                    wb.close()
                except Exception as e:
                    raise Exception(f"Invalid Excel file: {str(e)}")
                
                # Process the import with validation
                importer = ExcelWorkerImporter(temp_path, validate_only=True)
                
                # First, extract and preview the data with validation
                workers_data = importer.extract_workers_data()
                
                # Run validation check
                validation_results = importer.validate_data()
                
                pass
                
                # Convert image data to base64 for preview
                import base64
                preview_workers = []
                
                for w in workers_data[:10]:  # Preview first 10
                    worker_preview = {
                        'row': w['row'],
                        # All data fields from Excel columns A-S
                        'no': w['data'].get('no', ''),
                        'name': w['data'].get('name', ''),
                        'sex': w['data'].get('sex', ''),
                        'dob': w['data'].get('dob', ''),
                        'nationality': w['data'].get('nationality', ''),
                        'building': w['data'].get('building', ''),
                        'position': w['data'].get('position', ''),
                        'joined_date': w['data'].get('joined_date', ''),
                        'resigned_date': w['data'].get('resigned_date', ''),
                        'passport_no': w['data'].get('passport_no', ''),
                        'passport_dates': w['data'].get('passport_dates', ''),
                        'workpermit_dates': w['data'].get('workpermit_dates', ''),
                        'visa_dates': w['data'].get('visa_dates', ''),
                        'images': {}
                    }
                    
                    # Convert images to base64 for display
                    for col_letter, img_data in w['images'].items():
                        try:
                            img_base64 = base64.b64encode(img_data['data']).decode('utf-8')
                            # Determine image type from original name
                            img_ext = img_data['original_name'].lower().split('.')[-1] if '.' in img_data['original_name'] else 'jpg'
                            if img_ext in ['jpg', 'jpeg']:
                                mime_type = 'image/jpeg'
                            elif img_ext == 'png':
                                mime_type = 'image/png'
                            else:
                                mime_type = 'image/jpeg'  # Default
                            
                            worker_preview['images'][col_letter] = {
                                'data_url': f"data:{mime_type};base64,{img_base64}",
                                'original_name': img_data['original_name'],
                                'cell': img_data['cell'],
                                'size': len(img_data['data'])
                            }
                        except Exception as e:
                            pass
                    
                    preview_workers.append(worker_preview)
                
                # Store data in session for preview with validation results
                request.session['import_preview'] = {
                    'file_path': temp_path,
                    'worker_count': len(workers_data),
                    'update_existing': update_existing,
                    'skip_duplicates': skip_duplicates,
                    'workers': preview_workers,
                    'validation': validation_results  # Include validation results
                }
                
                return redirect('zone:import_workers_preview')

            except Exception as e:
                messages.error(request, f'Error processing Excel file: {str(e)}')
                # Only clean up temp file on error, not on success
                # (success case needs file for preview step)
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except OSError as e:
                        pass
        else:
            # Form is not valid
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        # Use simple form for testing if requested
        FormClass = SimpleExcelImportForm if request.GET.get('test') else WorkerExcelImportForm
        form = FormClass()
    
    context = {
        'form': form,
        'title': 'Import Workers from Excel',
    }
    
    # Use alternative templates 
    template = 'zone/import_workers_compact.html'  # Default to compact design
    if request.GET.get('minimal'):
        template = 'zone/import_workers_minimal.html'
    elif request.GET.get('classic'):
        template = 'zone/import_workers.html'
    elif request.GET.get('simple'):
        template = 'zone/import_workers_simple.html'
    elif request.GET.get('nojs'):
        template = 'zone/import_workers_nojs.html'
    
    return render(request, template, context)


@login_required
@permission_required('zone.add_worker', raise_exception=True)
def import_workers_preview(request):
    """Preview imported workers before confirming"""
    
    import_data = request.session.get('import_preview')
    if not import_data:
        messages.error(request, 'No import data found. Please upload a file first.')
        return redirect('zone:import_workers')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm':
            # Perform the actual import
            temp_path = import_data['file_path']
            
            try:
                importer = ExcelWorkerImporter(temp_path)
                results = importer.import_to_database(request.user)
                
                # Clean up temp file and session data
                try:
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                except OSError as e:
                    pass
                
                if 'import_preview' in request.session:
                    del request.session['import_preview']
                
                # Store detailed results in session for display
                request.session['import_results'] = {
                    'success_count': results['success_count'],
                    'error_count': results['error_count'],
                    'workers_created': results['workers_created'],
                    'validation_errors': results.get('validation_errors', []),
                    'warnings': results.get('warnings', [])
                }
                
                # Show appropriate message based on results
                if results['error_count'] > 0:
                    # Build detailed error message
                    error_msg = f'Import completed with issues: {results["success_count"]} workers imported, {results["error_count"]} failed.'
                    
                    # Add first few error details
                    if results.get('validation_errors'):
                        error_msg += '\n\nErrors:'
                        for err in results['validation_errors'][:3]:  # Show first 3 errors
                            error_msg += f'\n• Row {err["row"]} ({err["worker_name"]}): '
                            if err['errors']:
                                error_msg += err['errors'][0]['error']
                        
                        if len(results['validation_errors']) > 3:
                            error_msg += f'\n... and {len(results["validation_errors"]) - 3} more errors'
                    
                    messages.warning(request, error_msg)
                else:
                    success_msg = f'Successfully imported {results["success_count"]} workers.'
                    if results.get('warnings'):
                        success_msg += f' ({len(results["warnings"])} workers imported with warnings)'
                    messages.success(request, success_msg)
                
                return redirect('zone:import_workers_results')

            except Exception as e:
                messages.error(request, f'Error importing workers: {str(e)}')
                
                # Clean up
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
        elif action == 'cancel':
            # Cancel import and clean up
            temp_path = import_data['file_path']
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except OSError as e:
                pass
            
            if 'import_preview' in request.session:
                del request.session['import_preview']
            
            messages.info(request, 'Import cancelled.')
            return redirect('zone:import_workers')
    
    context = {
        'import_data': import_data,
        'title': 'Preview Import',
    }
    
    # Use full template by default, compact for mobile or when requested
    template = 'zone/import_workers_preview_full.html'
    if request.GET.get('compact'):
        template = 'zone/import_workers_preview.html'
    
    return render(request, template, context)


@login_required
def import_workers_results(request):
    """Display detailed import results with validation errors"""
    
    results = request.session.get('import_results')
    if not results:
        messages.info(request, 'No import results to display.')
        return redirect('zone:import_workers')
    
    # Clear results from session after displaying
    if request.method == 'POST':
        if 'import_results' in request.session:
            del request.session['import_results']
        return redirect('zone:worker_list')
    
    # Process results for display
    context = {
        'results': results,
        'title': 'Import Results',
        'has_errors': results.get('error_count', 0) > 0,
        'has_warnings': len(results.get('warnings', [])) > 0,
        'validation_errors': results.get('validation_errors', []),
        'warnings': results.get('warnings', [])
    }
    
    # Use ultra-compact template by default, with options for other views
    template = 'zone/import_workers_results_ultra.html'
    if request.GET.get('compact'):
        template = 'zone/import_workers_results_compact.html'
    elif request.GET.get('minimal'):
        template = 'zone/import_workers_results_minimal.html'
    elif request.GET.get('classic'):
        template = 'zone/import_workers_results.html'
    
    return render(request, template, context)


@login_required
@permission_required('zone.add_worker', raise_exception=True)
@require_http_methods(["POST"])
def import_workers_ajax(request):
    """AJAX endpoint for importing workers with progress updates"""
    
    form = WorkerExcelImportForm(request.POST, request.FILES)
    
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
    excel_file = form.cleaned_data['excel_file']
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        for chunk in excel_file.chunks():
            tmp_file.write(chunk)
        tmp_file.flush()
        temp_path = tmp_file.name
    
    try:
        with transaction.atomic():
            importer = ExcelWorkerImporter(temp_path)
            results = importer.import_to_database(request.user)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'success_count': results['success_count'],
                    'error_count': results['error_count'],
                    'errors': results['errors'][:5],  # First 5 errors
                    'workers_created': [
                        {'id': w['id'], 'name': w['name']} 
                        for w in results['workers_created'][:5]
                    ]
                }
            })

    except Exception as e:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@permission_required('zone.add_worker', raise_exception=True)
def download_template(request):
    """Download Excel template for worker import"""
    import os
    from django.conf import settings
    
    # Path to the sample Excel file
    template_path = os.path.join(settings.BASE_DIR, 'sample', 'worker_eform_medium.xlsx')

    if not os.path.exists(template_path):
        raise Http404("Template file not found")
    
    try:
        with open(template_path, 'rb') as template_file:
            response = HttpResponse(
                template_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="worker_import_template.xlsx"'
            return response
    except Exception as e:
        raise Http404("Could not serve template file")