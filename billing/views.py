from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import *
from .forms import (
    SignUpForm, BrandForm, ProductGroupForm, SupplierForm,
    ProductForm, CustomerForm, InvoiceForm, InvoiceDetailFormSet
)
from .mixins import ExportListMixin
from decimal import Decimal

# === REGISTRO ===
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('billing:brand_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# === BRAND (FBV) ===
@login_required
def brand_list(request):
    qs = Brand.objects.all()
    name = request.GET.get('name', '').strip()
    is_active = request.GET.get('is_active', '')
    if name:
        qs = qs.filter(name__icontains=name)
    if is_active in ('0', '1'):
        qs = qs.filter(is_active=is_active == '1')

    # Paginación manual
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    params.pop('page', None)

    # Export
    export = request.GET.get('export')
    if export in ('excel', 'pdf'):
        from .mixins import ExportListMixin
        class _Exp(ExportListMixin):
            model = Brand
            export_title = 'Marcas'
            export_fields = [
                ('Nombre', 'name'),
                ('Estado', lambda o: 'Activo' if o.is_active else 'Inactivo'),
                ('Creación', lambda o: o.created_at.strftime('%d/%m/%Y')),
            ]
            def get_queryset(self_inner):
                return qs
        exp = _Exp()
        if export == 'excel':
            return exp.export_excel()
        return exp.export_pdf()

    return render(request, 'billing/brand_list.html', {
        'brands': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
        'search_params': params.urlencode(),
    })

@login_required
def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca creada exitosamente!')
            return redirect('billing:brand_list')
    else:
        form = BrandForm()
    return render(request, 'billing/brand_form.html', {'form': form, 'title': 'Crear Marca'})

@login_required
def brand_update(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada exitosamente!')
            return redirect('billing:brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'billing/brand_form.html', {'form': form, 'title': 'Editar Marca'})

@login_required
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        brand.delete()
        messages.success(request, 'Marca eliminada exitosamente!')
        return redirect('billing:brand_list')
    return render(request, 'billing/brand_confirm_delete.html', {'object': brand})


# === PRODUCTGROUP (CBV) ===
class ProductGroupListView(ExportListMixin, LoginRequiredMixin, ListView):
    model = ProductGroup
    template_name = 'billing/product_group_list.html'
    context_object_name = 'items'
    paginate_by = 10

    export_title = 'Grupos de Productos'
    export_fields = [
        ('Nombre', 'name'),
        ('Estado', lambda o: 'Activo' if o.is_active else 'Inactivo'),
        ('Creación', lambda o: o.created_at.strftime('%d/%m/%Y')),
    ]

    def get_queryset(self):
        qs = ProductGroup.objects.all()
        g = self.request.GET
        if name := g.get('name', '').strip():
            qs = qs.filter(name__icontains=name)
        if (is_active := g.get('is_active', '')) in ('0', '1'):
            qs = qs.filter(is_active=is_active == '1')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['search_params'] = params.urlencode()
        return ctx

class ProductGroupCreateView(LoginRequiredMixin, CreateView):
    model = ProductGroup; form_class = ProductGroupForm
    template_name = 'billing/product_group_form.html'
    success_url = reverse_lazy('billing:productgroup_list')

class ProductGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductGroup; form_class = ProductGroupForm
    template_name = 'billing/product_group_form.html'
    success_url = reverse_lazy('billing:productgroup_list')

class ProductGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = ProductGroup
    template_name = 'billing/product_group_confirm_delete.html'
    success_url = reverse_lazy('billing:productgroup_list')


# === SUPPLIER (CBV) ===
class SupplierListView(ExportListMixin, LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'billing/supplier_list.html'
    context_object_name = 'items'
    paginate_by = 10

    export_title = 'Proveedores'
    export_fields = [
        ('Nombre', 'name'),
        ('Contacto', lambda o: o.contact_name or '-'),
        ('Email', lambda o: o.email or '-'),
        ('Teléfono', lambda o: o.phone or '-'),
        ('Estado', lambda o: 'Activo' if o.is_active else 'Inactivo'),
    ]

    def get_queryset(self):
        qs = Supplier.objects.all()
        g = self.request.GET
        if name := g.get('name', '').strip():
            qs = qs.filter(name__icontains=name)
        if email := g.get('email', '').strip():
            qs = qs.filter(email__icontains=email)
        if (is_active := g.get('is_active', '')) in ('0', '1'):
            qs = qs.filter(is_active=is_active == '1')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['search_params'] = params.urlencode()
        return ctx

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier; form_class = SupplierForm
    template_name = 'billing/supplier_form.html'
    success_url = reverse_lazy('billing:supplier_list')

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier; form_class = SupplierForm
    template_name = 'billing/supplier_form.html'
    success_url = reverse_lazy('billing:supplier_list')

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'billing/supplier_confirm_delete.html'
    success_url = reverse_lazy('billing:supplier_list')


# === PRODUCT (CBV) ===
class ProductListView(ExportListMixin, LoginRequiredMixin, ListView):
    model = Product
    template_name = 'billing/product_list.html'
    context_object_name = 'items'
    paginate_by = 3

    export_title = 'Productos'
    export_fields = [
        ('Nombre', 'name'),
        ('Marca', 'brand.name'),
        ('Grupo', 'group.name'),
        ('Precio', lambda o: f'{o.unit_price:.2f}'),
        ('Stock', 'stock'),
        ('Proveedores', lambda o: ', '.join(s.name for s in o.suppliers.all()) or '-'),
        ('Estado', lambda o: 'Activo' if o.is_active else 'Inactivo'),
    ]

    def get_queryset(self):
        qs = Product.objects.select_related('brand', 'group').prefetch_related('suppliers')
        g = self.request.GET
        if name := g.get('name', '').strip():
            qs = qs.filter(name__icontains=name)
        if brand := g.get('brand', ''):
            qs = qs.filter(brand_id=brand)
        if group := g.get('group', ''):
            qs = qs.filter(group_id=group)
        if price_min := g.get('price_min', '').strip():
            qs = qs.filter(unit_price__gte=price_min)
        if price_max := g.get('price_max', '').strip():
            qs = qs.filter(unit_price__lte=price_max)
        if stock_min := g.get('stock_min', '').strip():
            qs = qs.filter(stock__gte=stock_min)
        if stock_max := g.get('stock_max', '').strip():
            qs = qs.filter(stock__lte=stock_max)
        if (is_active := g.get('is_active', '')) in ('0', '1'):
            qs = qs.filter(is_active=is_active == '1')
        if supplier := g.get('supplier', ''):
            qs = qs.filter(suppliers__id=supplier).distinct()
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['brands'] = Brand.objects.order_by('name')
        ctx['groups'] = ProductGroup.objects.order_by('name')
        ctx['suppliers'] = Supplier.objects.order_by('name')
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['search_params'] = params.urlencode()
        return ctx

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product; form_class = ProductForm
    template_name = 'billing/product_form.html'
    success_url = reverse_lazy('billing:product_list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product; form_class = ProductForm
    template_name = 'billing/product_form.html'
    success_url = reverse_lazy('billing:product_list')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'billing/product_confirm_delete.html'
    success_url = reverse_lazy('billing:product_list')


# === CUSTOMER (CBV) ===
class CustomerListView(ExportListMixin, LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'billing/customer_list.html'
    context_object_name = 'items'
    paginate_by = 10

    export_title = 'Clientes'
    export_fields = [
        ('DNI/RUC', 'dni'),
        ('Apellido', 'last_name'),
        ('Nombre', 'first_name'),
        ('Email', lambda o: o.email or '-'),
        ('Teléfono', lambda o: o.phone or '-'),
        ('Estado', lambda o: 'Activo' if o.is_active else 'Inactivo'),
    ]

    def get_queryset(self):
        qs = Customer.objects.all()
        g = self.request.GET
        if name := g.get('name', '').strip():
            qs = qs.filter(first_name__icontains=name) | qs.filter(last_name__icontains=name)
        if dni := g.get('dni', '').strip():
            qs = qs.filter(dni__icontains=dni)
        if email := g.get('email', '').strip():
            qs = qs.filter(email__icontains=email)
        if (is_active := g.get('is_active', '')) in ('0', '1'):
            qs = qs.filter(is_active=is_active == '1')
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['search_params'] = params.urlencode()
        return ctx

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer; form_class = CustomerForm
    template_name = 'billing/customer_form.html'
    success_url = reverse_lazy('billing:customer_list')

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer; form_class = CustomerForm
    template_name = 'billing/customer_form.html'
    success_url = reverse_lazy('billing:customer_list')

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'billing/customer_confirm_delete.html'
    success_url = reverse_lazy('billing:customer_list')


# === INVOICE (CBV) ===
class InvoiceListView(ExportListMixin, LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'items'
    paginate_by = 10

    export_title = 'Facturas'
    export_fields = [
        ('#', 'id'),
        ('Cliente', lambda o: str(o.customer)),
        ('Fecha', lambda o: o.invoice_date.strftime('%d/%m/%Y %H:%M')),
        ('Subtotal', lambda o: f'{o.subtotal:.2f}'),
        ('Impuesto', lambda o: f'{o.tax:.2f}'),
        ('Total', lambda o: f'{o.total:.2f}'),
    ]

    def get_queryset(self):
        qs = Invoice.objects.select_related('customer')
        g = self.request.GET
        if customer := g.get('customer', '').strip():
            qs = qs.filter(
                customer__first_name__icontains=customer
            ) | qs.filter(customer__last_name__icontains=customer)
        if date_from := g.get('date_from', '').strip():
            qs = qs.filter(invoice_date__date__gte=date_from)
        if date_to := g.get('date_to', '').strip():
            qs = qs.filter(invoice_date__date__lte=date_to)
        if total_min := g.get('total_min', '').strip():
            qs = qs.filter(total__gte=total_min)
        if total_max := g.get('total_max', '').strip():
            qs = qs.filter(total__lte=total_max)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['search_params'] = params.urlencode()
        return ctx

@login_required
def invoice_create(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            subtotal = sum(d.subtotal for d in invoice.details.all())
            invoice.subtotal = subtotal
            invoice.tax = subtotal * Decimal('0.15')
            invoice.total = invoice.subtotal + invoice.tax
            invoice.save()
            messages.success(request, f'Factura #{invoice.id} creada! Total: ${invoice.total}')
            return redirect('billing:invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceDetailFormSet()
    return render(request, 'billing/invoice_form.html', {
        'form': form, 'formset': formset, 'title': 'Nueva Factura'
    })

class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'billing/invoice_confirm_delete.html'
    success_url = reverse_lazy('billing:invoice_list')
