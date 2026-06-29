# SALES_A2

Sistema web de gestión de ventas e inventario construido con Django 6.0.6.
Cubre el ciclo completo: catálogo de productos, gestión de clientes,
facturación de ventas y registro de compras a proveedores, con panel de
analíticas, exportación de datos y auditoría de acciones.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Framework | Django 6.0.6 |
| Base de datos | SQLite 3 (`dbsalesA2.sqlite3`) |
| Frontend | Bootstrap 5.3.0 + Bootstrap Icons (CDN) |
| Gráficos | Chart.js (CDN) |
| Formularios | django-widget-tweaks |
| Excel | openpyxl 3.1.5 |
| PDF | reportlab 4.5.1 |
| Imágenes | Pillow 12.2.0 |
| Shell/Dev | django-extensions, ipython |
| Idioma | `es-ec` / UTC |

---

## Estructura del proyecto

```
sale_a2_jhoan/
├── config/                  # Configuración central del proyecto
│   ├── settings.py
│   ├── urls.py              # Router raíz
│   ├── asgi.py
│   └── wsgi.py
├── billing/                 # App principal: catálogo y ventas
│   ├── models.py            # Brand, ProductGroup, Supplier, Product,
│   │                        #   Customer, CustomerProfile, Invoice, InvoiceDetail
│   ├── views.py             # 39 vistas (FBV y CBV)
│   ├── forms.py             # SignUpForm, BrandForm, ProductGroupForm,
│   │                        #   SupplierForm, CustomerForm, InvoiceForm,
│   │                        #   InvoiceDetailFormSet
│   ├── ProductForm.py       # ProductForm con validaciones personalizadas
│   ├── urls.py              # 58 rutas
│   ├── admin.py             # 6 ModelAdmin + 2 inlines
│   ├── *_column_config.py   # Config de columnas para cada módulo (6 archivos)
│   ├── migrations/
│   └── templates/billing/   # 27 plantillas HTML
├── purchasing/              # App de compras a proveedores
│   ├── models.py            # Purchase, PurchaseDetail
│   ├── views.py             # 5 vistas
│   ├── forms.py             # PurchaseForm, PurchaseDetailFormSet
│   ├── urls.py              # 5 rutas
│   ├── column_config.py
│   ├── migrations/
│   └── templates/purchasing/ # 4 plantillas HTML
├── shared/                  # Utilidades reutilizables entre apps
│   ├── decorators.py        # audit_action
│   ├── mixins.py            # StaffRequiredMixin
│   ├── validators.py        # validate_cedula_ec
│   ├── export_mixins.py     # ExportListMixin (genérico)
│   ├── column_export.py     # Export respetando selector de columnas
│   └── sentencias_orm.py    # Referencia de 50+ ejemplos ORM
├── templates/
│   └── registration/
│       ├── login.html
│       └── signup.html
├── media/
│   └── products/            # Imágenes subidas por el usuario
├── manage.py
├── requirements.txt
└── dbsalesA2.sqlite3
```

---

## Modelos

### App `billing`

#### Brand — Marcas
| Campo | Tipo |
|---|---|
| name | CharField (único) |
| description | TextField |
| is_active | BooleanField |
| created_at / updated_at | DateTimeField (auto) |

#### ProductGroup — Categorías
| Campo | Tipo |
|---|---|
| name | CharField (único) |
| is_active | BooleanField |
| created_at / updated_at | DateTimeField (auto) |

#### Supplier — Proveedores
| Campo | Tipo |
|---|---|
| name | CharField |
| contact_name | CharField |
| email | EmailField |
| phone | CharField |
| address | TextField |
| is_active | BooleanField |
| created_at / updated_at | DateTimeField (auto) |

#### Product — Productos
| Campo | Tipo |
|---|---|
| name | CharField |
| description | TextField |
| brand | FK → Brand |
| group | FK → ProductGroup |
| suppliers | M2M → Supplier |
| unit_price | DecimalField |
| stock | IntegerField |
| image | ImageField (`media/products/`) |
| is_active | BooleanField |
| created_at / updated_at | DateTimeField (auto) |

Propiedad calculada: `balance = unit_price × stock`.

#### Customer — Clientes
| Campo | Tipo |
|---|---|
| dni | CharField (único, validado) |
| first_name / last_name | CharField |
| email | EmailField |
| phone | CharField |
| address | TextField |
| is_active | BooleanField |
| created_at / updated_at | DateTimeField (auto) |

Propiedad: `full_name`. Validación de cédula ecuatoriana con `validate_cedula_ec`.

#### CustomerProfile — Perfil extendido del cliente (1:1)
| Campo | Tipo |
|---|---|
| taxpayer_type | CharField — `final / ruc / rise` |
| payment_terms | CharField — `cash / credit_15 / credit_30 / credit_60` |
| credit_limit | DecimalField |
| notes | TextField |

#### Invoice — Facturas de venta
| Campo | Tipo |
|---|---|
| customer | FK → Customer |
| invoice_date | DateTimeField (auto) |
| subtotal / tax / total | DecimalField |
| is_active | BooleanField |

#### InvoiceDetail — Líneas de factura
| Campo | Tipo |
|---|---|
| invoice | FK → Invoice |
| product | FK → Product |
| quantity | IntegerField |
| unit_price | DecimalField |
| subtotal | DecimalField (auto-calculado en `save`) |

### App `purchasing`

#### Purchase — Cabecera de compra
| Campo | Tipo |
|---|---|
| supplier | FK → Supplier |
| document_number | CharField |
| purchase_date | DateTimeField (auto) |
| subtotal / tax / total | DecimalField |
| is_active | BooleanField |

Restricción: `UniqueConstraint(supplier, document_number)` — no se puede
registrar el mismo número de documento dos veces para el mismo proveedor.

#### PurchaseDetail — Líneas de compra
| Campo | Tipo |
|---|---|
| purchase | FK → Purchase |
| product | FK → Product |
| quantity | PositiveIntegerField |
| unit_cost | DecimalField |
| subtotal | DecimalField (auto-calculado en `save`) |

---

## Funcionalidades

### Panel principal (Dashboard)

Vista `home` en `/` — requiere sesión.

- **10 tarjetas resumen** clicables: Productos, Categorías, Marcas,
  Proveedores, Clientes, Usuarios, Ventas, Ingresos, Stock bajo, Compras.
- **4 gráficos con Chart.js**: ventas por mes, productos más vendidos,
  distribución por categoría, estado del stock.
- **Alertas del sistema**: stock bajo, productos agotados, ventas del día,
  nuevos clientes.
- **Actividad reciente**: últimas ventas, productos agregados, usuarios
  registrados.

### Autenticación

- Registro de usuario (`/signup/`) con nombre, apellido y email — inicio de
  sesión automático tras el registro.
- Login y logout (`/accounts/login/`, `/accounts/logout/`).
- Logout por `POST` con token CSRF (no por enlace GET).
- Todas las vistas requieren sesión (`@login_required` / `LoginRequiredMixin`).

### CRUD de entidades

Cada entidad tiene: listado, creación, detalle, edición y eliminación.
La eliminación requiere usuario staff (`StaffRequiredMixin`).

| Módulo | URL base | Tipo de vista |
|---|---|---|
| Marcas | `/brands/` | FBV |
| Categorías | `/groups/` | CBV |
| Proveedores | `/suppliers/` | CBV |
| Productos | `/products/` | CBV |
| Clientes | `/customers/` | CBV |
| Facturas | `/invoices/` | CBV + FBV |
| Compras | `/purchases/` | FBV |

### Facturación (`Invoice`)

- Formulario de cabecera + **formset dinámico** de líneas (agregar/quitar
  productos sin recargar la página).
- Al seleccionar un producto, su precio y stock se cargan automáticamente vía
  la API JSON `/api/product-info/<pk>/`.
- Validación de stock disponible antes de confirmar.
- Al guardar: descuenta el stock de cada producto y calcula subtotal + IVA
  (15%) + total.

### Compras (`Purchase`)

- Cabecera + **formset dinámico** de líneas (3 líneas por defecto, ampliable).
- Cálculo automático de subtotal, IVA (15%) y total.
- Al confirmar una compra, el stock se incrementa con `F('stock') + cantidad`
  (seguro ante condiciones de carrera).
- No permite duplicar número de documento por proveedor.
- Filtros: proveedor, número de documento, rango de fechas.

### Validación de cédula ecuatoriana

`shared/validators.py → validate_cedula_ec` implementa el algoritmo oficial
del Registro Civil:

- Acepta cédula de 10 dígitos o RUC de 13 dígitos.
- Valida código de provincia (01–24).
- Valida tercer dígito < 6.
- Calcula y verifica el dígito verificador con módulo 10.

Se aplica en el formulario web y en el admin de Django.

### Validaciones de producto (`billing/ProductForm.py`)

- `unit_price` debe ser mayor a 0.
- `stock` debe ser mayor o igual a 0.
- `image`: tipo de archivo permitido (jpeg/png/gif/webp) y tamaño máximo de
  5 MB.
- Imagen actualizable de forma independiente vía AJAX (`/products/<pk>/update-image/`).

### Selector de columnas

Todos los listados tienen un modal para elegir qué columnas mostrar. La
selección se guarda en la sesión del usuario y se respeta al exportar a
PDF/Excel.

Cada módulo define sus columnas disponibles en su propio archivo
`<modulo>_column_config.py`, con la siguiente estructura:

```python
# billing/supplier_column_config.py
SUPPLIER_COLUMNS = {
    'name':  {'label': 'Nombre', 'visible': True,  'required': True, 'type': 'text'},
    'email': {'label': 'Email',  'visible': True,  'required': False, 'type': 'text'},
    ...
}
```

Módulos con selector: Productos (13 columnas), Marcas (6), Categorías (5),
Proveedores (9), Clientes (12), Facturas (8), Compras (9).

La actualización de columnas se hace vía AJAX a
`/<modulo>/api/update-visible-columns/`.

### Búsqueda, filtros y paginación

Cada listado tiene filtros específicos según el tipo de dato:

| Módulo | Filtros disponibles |
|---|---|
| Marcas | Nombre, estado |
| Categorías | Nombre, estado |
| Proveedores | Nombre, email, estado |
| Productos | Nombre, marca, categoría, proveedor, rango de precio, rango de stock |
| Clientes | Nombre, cédula, email, estado |
| Facturas | Cliente, rango de fechas, rango de total |
| Compras | Proveedor, número de documento, rango de fechas |

La paginación conserva los filtros activos al cambiar de página.

### Exportación a PDF y Excel

Botones **Listado PDF** y **Listado Excel** en cada módulo. Exportan
**todos los registros filtrados** (no solo la página actual) y respetan las
columnas elegidas en el selector.

- `shared/export_mixins.py → ExportListMixin`: exportación genérica para
  cualquier `ListView`, con columnas fijas:

  ```python
  from shared.export_mixins import ExportListMixin

  class ProductGroupListView(ExportListMixin, LoginRequiredMixin, ListView):
      export_title  = 'Categorías'
      export_fields = [
          ('Nombre', 'name'),
          ('Estado', lambda o: 'Activo' if o.is_active else 'Inactivo'),
      ]
  ```

- `shared/column_export.py → export_visible_columns_excel / export_visible_columns_pdf`:
  usado por los módulos con selector de columnas, genera el Excel/PDF a
  partir de la lista de columnas activas en sesión.

Excel usa `openpyxl` con estilos (fuente, relleno de cabecera, bordes,
ancho automático). PDF usa `reportlab` en A4 horizontal con tamaño de fuente
dinámico según número de columnas.

### Seguridad y auditoría

- Todas las vistas requieren sesión iniciada.
- Eliminación restringida a usuarios staff (`StaffRequiredMixin` en CBV;
  verificación equivalente en FBV como `purchase_delete`).
- `shared/decorators.py → audit_action(action_name)`: registra en consola
  cada acción relevante con timestamp, usuario, método HTTP, IP y ruta.
- Logout por `POST` con CSRF.

### API interna

| Endpoint | Descripción |
|---|---|
| `GET /api/product-info/<pk>/` | Retorna `{id, name, unit_price, stock}` en JSON para el formulario de facturas |

---

## Utilidades en `shared/`

| Archivo | Qué provee |
|---|---|
| `decorators.py` | `@audit_action('NOMBRE')` — log de auditoría para cualquier vista |
| `mixins.py` | `StaffRequiredMixin` — restringe acceso a usuarios staff |
| `validators.py` | `validate_cedula_ec` — validador de cédula/RUC ecuatoriano |
| `export_mixins.py` | `ExportListMixin` — exportación genérica Excel/PDF para ListView |
| `column_export.py` | Exportación dinámica respetando el selector de columnas |
| `sentencias_orm.py` | Referencia interna con 50+ ejemplos ORM (CREATE/READ/UPDATE/DELETE, relaciones, agregaciones) |

---

## Admin de Django

Accesible en `/admin/`. Incluye:

- **billing**: Brand, ProductGroup, Supplier (con inline de Product), Product,
  Customer (con inline de CustomerProfile), Invoice (con inline de
  InvoiceDetail).
- **purchasing**: Purchase (con inline de PurchaseDetail).

---

## Rutas completas

### `billing/urls.py` (58 rutas)

```
/                                          → home (dashboard)
/signup/                                   → SignUpView

/brands/                                   → brand_list
/brands/create/                            → brand_create
/brands/<pk>/                              → brand_detail
/brands/<pk>/edit/                         → brand_update
/brands/<pk>/delete/                       → brand_delete
/brands/api/update-visible-columns/        → brand_update_visible_columns

/groups/                                   → ProductGroupListView
/groups/create/                            → ProductGroupCreateView
/groups/<pk>/                              → ProductGroupDetailView
/groups/<pk>/edit/                         → ProductGroupUpdateView
/groups/<pk>/delete/                       → ProductGroupDeleteView
/groups/api/update-visible-columns/        → productgroup_update_visible_columns

/suppliers/                                → SupplierListView
/suppliers/create/                         → SupplierCreateView
/suppliers/<pk>/                           → SupplierDetailView
/suppliers/<pk>/edit/                      → SupplierUpdateView
/suppliers/<pk>/delete/                    → SupplierDeleteView
/suppliers/api/update-visible-columns/     → supplier_update_visible_columns

/products/                                 → ProductListView
/products/create/                          → ProductCreateView
/products/<pk>/                            → ProductDetailView
/products/<pk>/update-image/               → product_update_image (AJAX)
/products/<pk>/edit/                       → ProductUpdateView
/products/<pk>/delete/                     → ProductDeleteView
/products/api/update-visible-columns/      → product_update_visible_columns

/customers/                                → CustomerListView
/customers/create/                         → CustomerCreateView
/customers/<pk>/                           → CustomerDetailView
/customers/<pk>/edit/                      → CustomerUpdateView
/customers/<pk>/delete/                    → CustomerDeleteView
/customers/api/update-visible-columns/     → customer_update_visible_columns

/invoices/                                 → InvoiceListView
/invoices/create/                          → invoice_create
/invoices/<pk>/                            → InvoiceDetailView
/invoices/<pk>/delete/                     → InvoiceDeleteView
/invoices/api/update-visible-columns/      → invoice_update_visible_columns

/api/product-info/<pk>/                    → api_product_info (JSON)
```

### `purchasing/urls.py` (5 rutas)

```
/purchases/                                → purchase_list
/purchases/create/                         → purchase_create
/purchases/<pk>/                           → purchase_detail
/purchases/<pk>/delete/                    → purchase_delete
/purchases/api/update-visible-columns/     → purchase_update_visible_columns
```

### `config/urls.py`

```
/admin/        → Django admin
/accounts/     → Django auth (login, logout)
/purchases/    → purchasing.urls
/              → billing.urls
```

---

## Cómo ejecutar el proyecto

### 1. Crear el entorno virtual

```cmd
py -m venv ent_sales_a2
```

> Si `py` no funciona, usa `python` en su lugar.

### 2. Activar el entorno virtual

```cmd
ent_sales_a2\Scripts\activate.bat
```

### 3. Instalar las dependencias

```cmd
pip install -r requirements.txt
```

### 4. Aplicar las migraciones

```cmd
ent_sales_a2\Scripts\python.exe manage.py migrate
```

### 5. Crear un usuario administrador

Necesario para iniciar sesión la primera vez (todas las páginas requieren
sesión activa). Solo un usuario staff puede eliminar registros

```cmd
ent_sales_a2\Scripts\python.exe manage.py createsuperuser
```

### 6. Ejecutar el servidor

```cmd
ent_sales_a2\Scripts\python.exe manage.py runserver
```

Abre el navegador en: http://127.0.0.1:8000
