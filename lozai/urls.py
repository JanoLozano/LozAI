from django.contrib import admin
from django.urls import path
from sistema.controllers.usuario_controller import (
    listar_usuarios, 
    editar_usuario,
    cambiar_estado_usuario
)
from sistema.controllers.dashboard_controller import (
    dashboard,
    dashboard_admin,
    dashboard_tecnico,
    dashboard_usuario
)
from sistema.controllers.auth_controller import (
    login_view, 
    logout_view,
    register_view)
from sistema.controllers.maquina_controller import (
    listar_maquinas,
    chat_maquina,
    crear_maquina,
    editar_maquina,
    eliminar_maquina
)
from sistema.controllers.ticket_controller import (
    mis_tickets_usuario,
    detalle_mi_ticket,
    detalle_ticket,
    listar_tickets,
    crear_ticket,
    cambiar_estado_ticket
)

urlpatterns = [
    # Rutas para el panel de control
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    # Rutas para la gestión de máquinas
    path('maquinas/', listar_maquinas, name='listar_maquinas'),
    path('maquinas/<int:maquina_id>/chat/', chat_maquina, name='chat_maquina'),
    path('maquinas/crear/', crear_maquina, name='crear_maquina'),
    path('maquinas/<int:maquina_id>/editar/', editar_maquina, name='editar_maquina'),
    path('maquinas/<int:maquina_id>/eliminar/', eliminar_maquina, name='eliminar_maquina'),
    # Rutas para la gestión de tickets
    path('tickets/', listar_tickets, name='listar_tickets'),
    path('tickets/crear_ticket/', crear_ticket, name='crear_ticket'),   
    path('tickets/<int:ticket_id>/cambiar_estado/', cambiar_estado_ticket, name='cambiar_estado_ticket'),
    path('tickets/<int:ticket_id>/', detalle_ticket, name='detalle_ticket'),
    path('tickets/usuario/<int:usuario_id>/', mis_tickets_usuario, name='mis_tickets_usuario'),
    path('tickets/usuario/<int:usuario_id>/ticket/<int:ticket_id>/', detalle_mi_ticket, name='detalle_mi_ticket'),
    # Rutas para autenticación
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    # Rutas para los dashboards según el rol del usuario
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/tecnico/', dashboard_tecnico, name='dashboard_tecnico'),
    path('dashboard/usuario/', dashboard_usuario, name='dashboard_usuario'),
    # Rutas para la gestión de usuarios
    path('usuarios/', listar_usuarios, name='listar_usuarios'),
    path('usuarios/<int:usuario_id>/editar/', editar_usuario, name='editar_usuario'),
    path('usuarios/<int:usuario_id>/eliminar/', cambiar_estado_usuario, name='cambiar_estado_usuario'),
]