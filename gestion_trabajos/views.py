from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Sum
from .models import Trabajo, Pago, Cliente
from .forms import RegistroUsuarioForm, TrabajoForm, PagoForm, ClienteForm
from django.db.models import Q

def login_usuario(request):
    """Vista para el login de usuarios"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bienvenido {username}")
                return redirect('dashboard')
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    else:
        form = AuthenticationForm()
    
    return render(request, 'gestion_trabajos/login.html', {'form': form})

def registro_usuario(request):
    """Vista para el registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Usuario registrado correctamente")
            return redirect('dashboard')
        else:
            messages.error(request, "Error en el registro. Verifica los datos.")
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'gestion_trabajos/registro.html', {'form': form})

@login_required
def logout_usuario(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.info(request, "Sesión cerrada correctamente")
    return redirect('login')

@login_required
def dashboard(request):
    """Dashboard principal - solo usuarios autenticados"""
    trabajos = Trabajo.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Obtener parámetros de filtrado
    cliente_filtro = request.GET.get('cliente')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    estado_filtro = request.GET.get('estado')
    
    # Aplicar filtros
    if cliente_filtro:
        trabajos = trabajos.filter(cliente_id=cliente_filtro)
    
    if fecha_desde:
        trabajos = trabajos.filter(fecha_creacion__date__gte=fecha_desde)
    
    if fecha_hasta:
        trabajos = trabajos.filter(fecha_creacion__date__lte=fecha_hasta)
    
    if estado_filtro:
        trabajos = trabajos.filter(estado=estado_filtro)
    
    # Obtener todos los clientes para el filtro
    clientes = Cliente.objects.all().order_by('nombre')
    
    # Estadísticas del usuario (basadas en trabajos filtrados)
    total_trabajos = trabajos.count()
    trabajos_pendientes = trabajos.filter(estado='pendiente').count()
    trabajos_completados = trabajos.filter(estado='completado').count()
    
    # Calcular totales
    total_facturado = trabajos.aggregate(Sum('valor_total'))['valor_total__sum'] or 0
    total_cobrado = sum([trabajo.valor_total - trabajo.saldo for trabajo in trabajos])
    
    context = {
        'trabajos': trabajos[:50],  # Mostrar hasta 50 trabajos
        'clientes': clientes,
        'total_trabajos': total_trabajos,
        'trabajos_pendientes': trabajos_pendientes,
        'trabajos_completados': trabajos_completados,
        'total_facturado': total_facturado,
        'total_cobrado': total_cobrado,
        # Mantener valores de filtros para el template
        'cliente_filtro': cliente_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estado_filtro': estado_filtro,
    }
    
    return render(request, 'gestion_trabajos/dashboard.html', context)

@login_required
def registrar_cliente(request):
    """Registrar nuevo cliente - solo usuarios autenticados"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.nombre} registrado exitosamente.')
            return redirect('lista_clientes')
        else:
            messages.error(request, "Error al registrar cliente. Verifica los datos.")
    else:
        form = ClienteForm()
    
    return render(request, 'gestion_trabajos/registrar_cliente.html', {'form': form})

@login_required
def lista_clientes(request):
    """Lista de clientes - solo usuarios autenticados"""
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'gestion_trabajos/lista_clientes.html', {'clientes': clientes})

@login_required
def detalle_cliente(request, cliente_id):
    """Detalle de cliente - solo usuarios autenticados"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    trabajos = Trabajo.objects.filter(cliente=cliente, usuario=request.user)
    
    return render(request, 'gestion_trabajos/detalle_cliente.html', {
        'cliente': cliente,
        'trabajos': trabajos
    })

@login_required
def nuevo_trabajo(request):
    """Crear nuevo trabajo - solo usuarios autenticados"""
    if request.method == 'POST':
        form = TrabajoForm(request.POST)
        if form.is_valid():
            trabajo = form.save(commit=False)
            trabajo.usuario = request.user
            trabajo.saldo = trabajo.valor_total
            
            # Generar número de factura automáticamente si requiere factura
            if trabajo.requiere_factura:
                # Obtener el último número de factura
                ultimo_trabajo_con_factura = Trabajo.objects.filter(
                    factura_electronica__isnull=False
                ).exclude(factura_electronica='').order_by('-id').first()
                
                if ultimo_trabajo_con_factura and ultimo_trabajo_con_factura.factura_electronica.isdigit():
                    ultimo_numero = int(ultimo_trabajo_con_factura.factura_electronica)
                    nuevo_numero = ultimo_numero + 1
                else:
                    nuevo_numero = 1
                
                # Formatear a 3 dígitos con ceros a la izquierda
                trabajo.factura_electronica = f"{nuevo_numero:03d}"
            
            trabajo.save()
            messages.success(request, "Trabajo registrado correctamente")
            return redirect('dashboard')
        else:
            messages.error(request, "Error al crear trabajo. Verifica los datos.")
    else:
        form = TrabajoForm()
    
    return render(request, 'gestion_trabajos/form_trabajo.html', {
        'form': form,
        'titulo': 'Nuevo Trabajo'
    })

@login_required
def editar_trabajo(request, trabajo_id):
    """Editar trabajo existente - solo usuarios autenticados y propietarios"""
    trabajo = get_object_or_404(Trabajo, id=trabajo_id, usuario=request.user)
    
    if request.method == 'POST':
        form = TrabajoForm(request.POST, instance=trabajo)
        if form.is_valid():
            # Guardar el valor total anterior para recalcular el saldo
            valor_total_anterior = trabajo.valor_total
            
            trabajo = form.save(commit=False)
            
            # Recalcular saldo si el valor total cambió
            if trabajo.valor_total != valor_total_anterior:
                total_pagos = trabajo.pagos.aggregate(Sum('monto'))['monto__sum'] or 0
                trabajo.saldo = trabajo.valor_total - total_pagos
            
            trabajo.save()
            messages.success(request, "Trabajo actualizado correctamente")
            return redirect('detalle_trabajo', trabajo_id=trabajo.id)
        else:
            messages.error(request, "Error al actualizar trabajo. Verifica los datos.")
    else:
        form = TrabajoForm(instance=trabajo)
    
    return render(request, 'gestion_trabajos/form_trabajo.html', {
        'form': form,
        'titulo': f'Editar Trabajo #{trabajo.id}',
        'trabajo': trabajo
    })

@login_required
def detalle_trabajo(request, trabajo_id):
    """Detalle de trabajo - solo usuarios autenticados y propietarios"""
    trabajo = get_object_or_404(Trabajo, id=trabajo_id, usuario=request.user)
    pagos = trabajo.pagos.all().order_by('-fecha')
    
    return render(request, 'gestion_trabajos/detalle_trabajo.html', {
        'trabajo': trabajo,
        'pagos': pagos
    })

@login_required
def registrar_pago(request, trabajo_id):
    """Registrar pago - solo usuarios autenticados y propietarios del trabajo"""
    trabajo = get_object_or_404(Trabajo, id=trabajo_id, usuario=request.user)
    
    if trabajo.saldo <= 0:
        messages.info(request, "Este trabajo ya está pagado completamente")
        return redirect('detalle_trabajo', trabajo_id=trabajo.id)
    
    if request.method == 'POST':
        form = PagoForm(trabajo, request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.trabajo = trabajo
            pago.save()
            
            # El saldo se actualiza automáticamente en el método save() de Pago
            messages.success(request, f"Pago de ${pago.monto} registrado correctamente")
            return redirect('detalle_trabajo', trabajo_id=trabajo.id)
        else:
            messages.error(request, "Error al registrar pago. Verifica los datos.")
    else:
        form = PagoForm(trabajo)
    
    return render(request, 'gestion_trabajos/registrar_pago.html', {
        'form': form,
        'trabajo': trabajo
    })
    
@login_required
def buscar_trabajos(request):
    
    # Obtener todos los clientes para el dropdown
    clientes = Cliente.objects.all()
    
    # Inicializar queryset con todos los trabajos
    trabajos = Trabajo.objects.all()
    
    # Variables para mantener los valores en el formulario
    busqueda_texto = request.GET.get('busqueda', '')
    cliente_filtro = request.GET.get('cliente', '')
    estado_filtro = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    # Aplicar filtros
    if busqueda_texto:
        trabajos = trabajos.filter(
            Q(descripcion__icontains=busqueda_texto) |
            Q(cliente__nombre__icontains=busqueda_texto)
        )
    
    if cliente_filtro:
        trabajos = trabajos.filter(cliente_id=cliente_filtro)
    
    if estado_filtro:
        trabajos = trabajos.filter(estado=estado_filtro)
    
    if fecha_desde:
        trabajos = trabajos.filter(fecha_creacion__gte=fecha_desde)
    
    if fecha_hasta:
        trabajos = trabajos.filter(fecha_creacion__lte=fecha_hasta)
    
    # Calcular estadísticas
    total_trabajos = trabajos.count()
    trabajos_pendientes = trabajos.filter(estado='Pendiente').count()
    trabajos_proceso = trabajos.filter(estado='En Proceso').count()
    trabajos_terminados = trabajos.filter(estado='Terminado').count()
    trabajos_entregados = trabajos.filter(estado='Entregado').count()
    
    context = {
        'trabajos': trabajos,
        'clientes': clientes,
        'total_trabajos': total_trabajos,
        'trabajos_pendientes': trabajos_pendientes,
        'trabajos_proceso': trabajos_proceso,
        'trabajos_terminados': trabajos_terminados,
        'trabajos_entregados': trabajos_entregados,
        'busqueda_texto': busqueda_texto,
        'cliente_filtro': cliente_filtro,
        'estado_filtro': estado_filtro,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    
    return render(request, 'gestion_trabajos/buscar_trabajos.html', context)
