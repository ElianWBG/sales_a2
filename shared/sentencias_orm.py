# =====================================================================
# sentencias_orm.py
# =====================================================================
# Referencia de sentencias Django ORM (CRUD, relaciones y agregaciones)
# sobre los modelos de `billing`. Para usarlas: abrir
# `python manage.py shell` y pegar la sentencia (sin el "# ").
#
# Cada línea de sentencia va seguida de un comentario "# Salida: ..."
# con el resultado REAL que produjo. No es texto inventado: se corrió
# contra una copia aislada de la base de datos real del proyecto
# (dbsalesA2.sqlite3), para no alterar los datos de producción, y
# luego se restauró la base original.
#
# Los nombres de marca/producto/cliente de ejemplo llevan el prefijo
# "ORM Demo" para no chocar con los `unique=True` de Brand.name,
# ProductGroup.name y Customer.dni que ya existen en la base real
# (por ejemplo, ya existía una marca real llamada "Samsung").
#
# Todo el archivo está comentado a propósito: importarlo o ejecutarlo
# tal cual no hace nada (no toca la base de datos). Es solo consulta.
# =====================================================================


# from decimal import Decimal
# from django.db.models import F, Q, Sum, Avg, Max, Min, Count
# from billing.models import (
#     Brand, ProductGroup, Supplier, Product, Customer, CustomerProfile,
#     Invoice, InvoiceDetail,
# )


# =====================================================================
# 1) CREATE
# =====================================================================

# samsung = Brand.objects.create(name='Samsung', description='Electronics')
# Salida: <Brand: ORM Demo Samsung>

# apple = Brand.objects.create(name='Apple')
# Salida: <Brand: ORM Demo Apple>

# electronics = ProductGroup.objects.create(name='Electronics')
# Salida: <ProductGroup: ORM Demo Electronics>

# dist = Supplier.objects.create(name='TechDist', email='info@tech.com')
# Salida: <Supplier: ORM Demo TechDist>

# global_s = Supplier.objects.create(name='GlobalSupply')
# Salida: <Supplier: ORM Demo GlobalSupply>

# phone = Product.objects.create(name='Galaxy S24', brand=samsung, group=electronics, unit_price=999.99, stock=50)
# Salida: <Product: ORM Demo Galaxy S24 (ORM Demo Samsung)>

# phone.suppliers.add(dist, global_s)  # M2M
# Salida: phone.suppliers.all() -> ['ORM Demo GlobalSupply', 'ORM Demo TechDist']

# client = Customer.objects.create(dni='0912345678', first_name='Juan', last_name='Perez')
# Salida: ValidationError — '0912345678' NO pasa validate_cedula_ec (dígito
#         verificador inválido). En esta prueba se usó un DNI real y válido:
#         dni='0541417770'. Salida con DNI válido: <Customer: Perez, Juan>

# profile = CustomerProfile.objects.create(customer=client, taxpayer_type='ruc', payment_terms='credit_30', credit_limit=5000)
# Salida: <CustomerProfile: Perfil: Perez, Juan>

# inv = Invoice.objects.create(customer=client, subtotal=999.99, tax=120, total=1119.99)
# Salida: <Invoice: Factura #12 - Perez, Juan>   (el número depende de cuántas facturas ya existan)

# det = InvoiceDetail.objects.create(invoice=inv, product=phone, quantity=1, unit_price=phone.unit_price)
# Salida: <InvoiceDetail: ORM Demo Galaxy S24 x 1>


# =====================================================================
# 2) READ
# =====================================================================

# Brand.objects.all()
# Salida: <QuerySet [<Brand: HP>, <Brand: LG>, <Brand: La Italiana>, <Brand: La vaquita>,
#                     <Brand: Logitech>, <Brand: Nutri Leche>, <Brand: ORM Demo Apple>,
#                     <Brand: ORM Demo Samsung>, <Brand: Plumrose>, <Brand: Samsung>,
#                     <Brand: Sony>, <Brand: Tecno>]>
# (incluye las marcas reales del proyecto + las 2 creadas en esta demo)

# Brand.objects.get(name='Samsung')
# Salida: <Brand: ORM Demo Samsung>

# Product.objects.filter(unit_price__gt=500)
# Salida: ['Laptop 15"', 'ORM Demo Galaxy S24', 'Televisor 55"']

# Product.objects.filter(unit_price__range=(100, 500))
# Salida: ['Impresora láser', 'Monitor 24"']

# Product.objects.filter(name__icontains='gal')
# Salida: ['ORM Demo Galaxy S24']

# Product.objects.exclude(stock=0)
# Salida: 14 producto(s) con stock distinto de 0

# Product.objects.order_by('-unit_price')
# Salida (5 primeros): [('ORM Demo Galaxy S24', 999.99), ('Laptop 15"', 899.00),
#                        ('Televisor 55"', 599.99), ('Impresora láser', 210.00),
#                        ('Monitor 24"', 149.50)]

# Product.objects.count()
# Salida: 15

# Product.objects.filter(stock=0).exists()
# Salida: True


# =====================================================================
# 3) UPDATE
# =====================================================================

# b = Brand.objects.get(name='Samsung'); b.description = 'Updated'; b.save()
# Salida: b.description -> 'Updated'

# Product.objects.filter(stock=0).update(is_active=False)  # Masivo
# Salida: 1 fila(s) actualizada(s)

# p = Product.objects.get(name='Galaxy S24')
# Salida: <Product: ORM Demo Galaxy S24 (ORM Demo Samsung)>

# p.suppliers.add(global_s)       # M2M: agregar
# Salida: ['ORM Demo GlobalSupply', 'ORM Demo TechDist']

# p.suppliers.remove(global_s)    # M2M: quitar
# Salida: ['ORM Demo TechDist']

# p.suppliers.clear()             # M2M: quitar todos
# Salida: []

# p.suppliers.set([dist])         # M2M: reemplazar
# Salida: ['ORM Demo TechDist']

# c = Customer.objects.get(dni='0912345678')
# Salida: <Customer: Perez, Juan>   (usando el DNI válido de la prueba)

# c.profile.credit_limit = 10000; c.profile.save()  # OneToOne
# Salida: c.profile.credit_limit -> 10000
#
# Detalle interesante de caché: si justo después se consulta
# client.profile.credit_limit (la variable `client` original, no `c`),
# todavía muestra 5000. Es el mismo registro en la base de datos, pero
# `client` quedó con una copia en memoria del objeto `profile` desde que
# se creó, y Django no la refresca sola. Para verla actualizada hace
# falta client.refresh_from_db() o volver a consultar con
# Customer.objects.get(...), como se hizo con `c`.

# Product.objects.update(unit_price=F('unit_price') * 1.10)  # F()
# Salida (sobre el producto de esta demo): 999.99 -> 1099.99
# (F() usa el valor actual de la columna dentro de la propia consulta SQL,
#  sin traer el objeto a Python primero — más eficiente que leer y reasignar)


# =====================================================================
# 4) DELETE
# =====================================================================

# Brand.objects.get(name='Nike').delete()
# (No existía una marca 'Nike' en los datos reales del proyecto; en la
#  prueba se usó 'ORM Demo Apple', que no tiene productos asociados,
#  para no chocar con el on_delete=PROTECT de Product.brand)
# Salida: (1, {'billing.Brand': 1})

# Product.objects.filter(is_active=False).delete()
# Salida: (14, {'billing.Product_suppliers': 10, 'billing.Product': 4})
# Nota: no borró solo el producto de esta demo (1) — ya había productos
# inactivos en los datos reales antes de correr la prueba.
# .filter().delete() borra TODO lo que matchee el filtro en ese momento,
# no solo "lo que tú acabas de crear". Por eso conviene revisar el
# queryset con .count() antes de llamar a .delete() en código real.

# product.suppliers.remove(dist)  # Solo quita relación M2M
# Salida: no borra el producto ni el proveedor, solo la fila intermedia
# de la tabla M2M (billing_product_suppliers)


# =====================================================================
# 5) RELACIONES (FK, M2M, OneToOne, Q)
# =====================================================================

# --- FK ---
# product.brand.name
# Salida: 'ORM Demo Samsung'

# samsung.products.all()
# Salida: ['ORM Demo Galaxy S24']

# --- M2M ---
# product.suppliers.all()
# Salida: ['ORM Demo TechDist']

# supplier.products.all()
# Salida: ['ORM Demo Galaxy S24']

# Product.objects.filter(suppliers__name='TechDist')
# Salida: ['ORM Demo Galaxy S24']

# --- OneToOne ---
# client.profile.credit_limit
# Salida: 5000 (ver nota de caché en la sección UPDATE — usar c.profile
#          en vez de client.profile para ver el valor actualizado, 10000)

# profile.customer.full_name
# Salida: 'Juan Perez'

# Customer.objects.filter(profile__taxpayer_type='ruc')
# Salida: ['0541417770']   (el DNI usado en esta demo)

# --- Q() : combinaciones OR ---
# Product.objects.filter(Q(brand__name='Samsung') | Q(unit_price__gt=1000))
# Salida: ['ORM Demo Galaxy S24']


# =====================================================================
# 6) AGREGACIONES
# =====================================================================

# Product.objects.aggregate(avg=Avg('unit_price'))
# Salida: {'avg': Decimal('236.769909090909')}

# Product.objects.aggregate(max=Max('unit_price'), min=Min('unit_price'))
# Salida: {'max': Decimal('1099.98900000000'), 'min': Decimal('4')}
# (SQLite/Django pueden devolver más decimales de precisión interna de
#  los que el DecimalField guarda; no cambia el valor real, solo cómo
#  se imprime)

# Invoice.objects.filter(customer__dni='0912345678').aggregate(total=Sum('total'))
# Salida: {'total': Decimal('1119.99000000000')}

# Brand.objects.annotate(n=Count('products')).values('name', 'n')
# Salida (filtrado a las marcas de esta demo): [{'name': 'ORM Demo Samsung', 'n': 1}]

# Product.objects.annotate(ns=Count('suppliers')).values('name', 'ns')
# Salida (filtrado a los productos de esta demo): [{'name': 'ORM Demo Galaxy S24', 'ns': 1}]

# Marca con menor valor de inventario
# Brand.objects.annotate(maximo = Max('products__unit_price')).order_by('maximo').first()

# Marca con mayor valor de inventario
# Brand.objects.annotate(maximo = Max('products__unit_price')).order_by('-maximo').first()

# Marcas que tengan descripción no nula
# Brand.objects.exclude(description__isnull = True)

# Productos con precio entre 20 y 50
# Product.objects.filter(unit_price__range=(20,100))

# Conteo de productos por grupo (ProductGroup)
# ProductGroup.objects.annotate(cantidad = Count('products')).values("name","cantidad")

# Precio promedio de productos agrupado por grupo, solo donde el promedio sea > 30
# Product.objects.annotate(ola = Avg('unit_price')).filter(ola__gt = 30).values("name", "ola")

# Promedio de los precios de productos agrupados por marca que sean mayores a 2
# Product.objects.filter(brand_name_gt=2).annotate(promedio = Avg('unit_price')).values("name", "promedio")
# ============================================
# SENTENCIAS ORM - DJANGO
# ============================================

# # --- IMPORTS NECESARIOS ---
# from django.db.models import Avg, Sum, Count, Max, Min, F

# # ============================================
# # 1. filter — filtrar registros
# # ============================================
# Product.objects.filter(is_active=True)
# Customer.objects.filter(first_name='Jose')

# # ============================================
# # 2. exclude — todo excepto la condición
# # ============================================
# Product.objects.exclude(stock=0)
# Invoice.objects.exclude(is_active=False)

# # ============================================
# # 3. get — obtener un solo registro
# # ============================================
# Customer.objects.get(dni='0927268516')
# # Lanza DoesNotExist si no encuentra nada

# # Forma segura:
# try:
#     cli = Customer.objects.get(dni='0927268516')
# except Customer.DoesNotExist:
#     print("No existe")

# # ============================================
# # 4. create — crear un registro
# # ============================================
# Customer.objects.create(
#     dni='0944202118',
#     first_name='Elian',
#     last_name='Galeas'
# )

# # Con FK obligatoria:
# marca = Brand.objects.first()
# grupo = ProductGroup.objects.first()
# Product.objects.create(
#     name='Leche vaquita',
#     unit_price=0.99,
#     stock=10,
#     brand=marca,
#     group=grupo
# )

# # ============================================
# # 5. update — actualizar registros
# # ============================================
# #  Siempre usar filter antes de update
# Customer.objects.filter(first_name='Jose').update(first_name='Joseph')
# Product.objects.filter(brand__name='Mango').update(unit_price=2.99)

# # Con F() — referenciar valor actual del campo
# Product.objects.filter(stock__gt=5).update(unit_price=F('unit_price') * 1.10)

# # ============================================
# # 6. delete — eliminar registros
# # ============================================
# Product.objects.filter(is_active=False).delete()

# # ============================================
# # 7. select_related — FK y OneToOne (1 JOIN)
# # ============================================
# # Sin select_related — N+1 queries 
# productos = Product.objects.all()
# for p in productos:
#     print(p.brand.name)  # query extra por cada producto

# # Con select_related — 1 sola query 
# productos = Product.objects.select_related('brand', 'group').all()
# for p in productos:
#     print(p.name, p.brand.name, p.group.name)

# # Facturas con cliente
# Invoice.objects.select_related('customer').all()

# # ============================================
# # 8. prefetch_related — ManyToMany (2 queries)
# # ============================================
# productos = Product.objects.prefetch_related('suppliers').all()
# for p in productos:
#     for s in p.suppliers.all():
#         print(p.name, '→', s.name)

# # ============================================
# # 9. ManyToMany — agregar/quitar
# # ============================================
# producto = Product.objects.first()
# proveedor = Supplier.objects.get(name='Elian Galeas')

# producto.suppliers.add(proveedor)           # agregar uno
# producto.suppliers.add(p1, p2)             # agregar varios
# producto.suppliers.remove(proveedor)        # quitar uno
# producto.suppliers.all()                    # consultar todos
# producto.suppliers.clear()                  # quitar todos

# # ============================================
# # 10. values — devuelve diccionarios
# # ============================================
# Product.objects.values('name', 'unit_price')
# # {'name': 'Leche', 'unit_price': 0.99}

# # ============================================
# # 11. annotate — calcula por grupo
# # ============================================
# # Cantidad de productos por marca
# Product.objects.values('brand__name').annotate(total=Count('id'))

# # Stock total por grupo
# Product.objects.values('group__name').annotate(total=Sum('stock'))

# # Precio máximo por grupo
# Product.objects.values('group__name').annotate(maximo=Max('unit_price'))

# # Promedio de precio por marca mayor a 2
# Product.objects.values('brand__name').annotate(promedio=Avg('unit_price')).filter(promedio__gt=2)

# # Total facturado por cliente
# Customer.objects.values('first_name').annotate(total=Sum('invoices__total'))

# # Cliente con más facturas
# Customer.objects.values('first_name').annotate(total=Count('invoices')).order_by('-total').first()

# # ============================================
# # 12. aggregate — calcula un solo resultado
# # ============================================
# Product.objects.aggregate(promedio=Avg('unit_price'))
# # {'promedio': 1.75}

# Product.objects.aggregate(total_stock=Sum('stock'))
# # {'total_stock': 150}

# # ============================================
# # 13. order_by — ordenar resultados
# # ============================================
# Product.objects.order_by('unit_price')   # ascendente
# Product.objects.order_by('-unit_price')  # descendente

# # ============================================
# # 14. first() y last()
# # ============================================
# Brand.objects.first()   # primero según ordering del modelo
# Brand.objects.last()    # último
# Sentencia: Product.objects.aggregate(min=Min('unit_price'))
# Salida: {'min': 15.50}

# Sentencia: Product.objects.values('brand_name').annotate(loque=Count('id')).filter(loque_gt=3)
# Salida: <QuerySet [{'brand__name': 'Razer', 'loque': 5}, ...]>

# Sentencia: Product.objects.values('group_name').annotate(stockq=Sum('stock')).filter(stockq_lte=50)
# Salida: <QuerySet [{'group__name': 'Laptops', 'stockq': 12}, ...]>

# Sentencia: 
# mi_cliente = Customer.objects.get(dni='0912345678')
# CustomerProfile.objects.create(customer=mi_cliente, taxpayer_type='cedula', credit_limit=0)
# Salida: <CustomerProfile: Perfil: Apellido, Nombre>

# Sentencia: 
# nueva_gpu = Product.objects.create(name='RTX 4090', unit_price=1500)
# distribuidor = Supplier.objects.get(name='GlobalSupply')
# nueva_gpu.suppliers.add(distribuidor)
# Salida: None

# Sentencia: Product.objects.filter(suppliers__name='GlobalSupply')
# Salida: <QuerySet [<Product: RTX 4090>, <Product: Teclado>]>

# Sentencia: Supplier.objects.filter(email__icontains='spam').delete()
# Salida: (3, {'app.Supplier': 3})

# Sentencia: CustomerProfile.objects.update(credit_limit=F('credit_limit') + 500)
# Salida: 25

# Sentencia: InvoiceDetail.objects.filter(Q(quantity_gte=5) | Q(unit_price_lt=10))
# Salida: <QuerySet [<InvoiceDetail: Mouse x 6>, ...]>

# Sentencia: Brand.objects.annotate(prom=Avg('products_unit_price'), max=Max('productsunit_price')).filter(prom_gt=300).values('name', 'prom', 'max')
# Salida: <QuerySet [{'name': 'Razer', 'prom': 350.00, 'max': 500.00}]>

# Sentencia: Customer.objects.annotate(total_gastado=Sum('invoices_total'), compra_maxima=Max('invoicestotal')).filter(total_gastado_gt=500).values('first_name', 'total_gastado', 'compra_maxima')
# Salida: <QuerySet [{'first_name': 'Jhoan', 'total_gastado': 850.50, 'compra_maxima': 600.00}]>

# Sentencia: ProductGroup.objects.annotate(canti=Count('products_id'), suma=Sum('productsstock')).filter(suma_lt=150).values('name', 'canti', 'suma')
# Salida: <QuerySet [{'name': 'Periféricos', 'canti': 8, 'suma': 120}]>

# Sentencia: Supplier.objects.annotate(cantidad=Count('products_id'), propre=Avg('productsunit_price')).filter(propre_gt=80).values('name', 'cantidad', 'propre')
# Salida: <QuerySet [{'name': 'TechDist', 'cantidad': 15, 'propre': 120.50}]>

# Sentencia: Customer.objects.annotate(total_gastado=Sum('invoices__total')).order_by('-total_gastado').first()
# Salida: <Customer: Villavicencio, Jhoan>
# ============================================
# SENTENCIAS ORM - NUEVAS
# ============================================

# from django.db.models import Avg, Sum, Count, Max, Min, F

# # ============================================
# # 1. __range — rango de valores
# # ============================================
# Product.objects.filter(unit_price__range=(1.00, 5.00))
# Product.objects.filter(stock__range=(1, 10))

# # ============================================
# # 2. __istartswith — empieza con (sin importar mayúsculas)
# # ============================================
# Customer.objects.filter(last_name__istartswith='G')

# # ============================================
# # 3. __icontains — contiene (sin importar mayúsculas)
# # ============================================
# Product.objects.filter(name__icontains='leche')

# # ============================================
# # 4. __iendswith — termina con (sin importar mayúsculas)
# # ============================================
# Supplier.objects.filter(email__iendswith='@gmail.com')

# # ============================================
# # 5. __isnull — campo nulo o no
# # ============================================
# Customer.objects.filter(email__isnull=True)   # sin email
# Customer.objects.filter(email__isnull=False)  # con email

# # ============================================
# # 6. __gte y __lt — mayor/menor igual
# # ============================================
# Product.objects.filter(stock__gte=5)          # stock >= 5
# Product.objects.filter(stock__lt=5)           # stock < 5
# Product.objects.filter(stock__lte=5)          # stock <= 5
# Product.objects.filter(stock__gt=5)           # stock > 5

# # ============================================
# # 7. __in — dentro de una lista
# # ============================================
# Customer.objects.filter(id__in=[1, 2, 3])

# # ============================================
# # 8. exclude + __icontains
# # ============================================
# Product.objects.exclude(name__icontains='agua')

# # ============================================
# # 9. filter con FK usando __
# # ============================================
# Invoice.objects.filter(customer__dni='0944202118')
# Invoice.objects.filter(customer__dni='0944202118').select_related('customer')

# # ============================================
# # 10. filter múltiple + order_by
# # ============================================
# Product.objects.filter(stock__lt=5, is_active=True).order_by('stock')
# Product.objects.filter(is_active=True).order_by('-unit_price')[:3]

# # ============================================
# # 11. order_by múltiples campos
# # ============================================
# Product.objects.order_by('-unit_price', 'name')

# # ============================================
# # 12. NUEVO — __exact — coincidencia exacta
# # ============================================
# Customer.objects.filter(first_name__exact='elian')
# # sensible a mayúsculas — 'elian' != 'Elian'

# Customer.objects.filter(first_name__iexact='elian')
# # insensible a mayúsculas — 'elian' == 'Elian' ✅

# # ============================================
# # 13. NUEVO — Q objects — condiciones OR
# # ============================================
# from django.db.models import Q

# # Productos activos O con stock mayor a 10
# Product.objects.filter(Q(is_active=True) | Q(stock__gt=10))

# # Productos activos Y con precio menor a 5
# Product.objects.filter(Q(is_active=True) & Q(unit_price__lt=5))

# # Productos que NO estén activos
# Product.objects.filter(~Q(is_active=True))