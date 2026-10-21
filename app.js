// ==========================================================================
// UNIVERSIDAD GERARDO BARRIOS - PROGRAMACIÓN COMPUTACIONAL III
// PARCIAL II - GESTIÓN DE USUARIOS Y AUTENTICACIÓN
// Estudiante: Jaime Salmeron (USSS014225)
// ==========================================================================

let usuarioAutenticado = null;
let listaUsuariosMemoria = [];
let temporizadorBusqueda = null;

// ==========================================================================
// 1. GESTIÓN DE SESIÓN Y VISTAS MODULARES (Requerimiento 5 y Rúbrica)
// "El login debe de ser el primero que se muestre al ejecutar el servidor"
// ==========================================================================

async function cargarVista(nombreVista) {
    const contenedor = document.getElementById('contenedorPrincipal');
    if (!contenedor) return;

    try {
        const respuesta = await fetch(`/vistas?form=${encodeURIComponent(nombreVista)}`);
        if (!respuesta.ok) {
            throw new Error(`Error HTTP ${respuesta.status}: No se pudo cargar el módulo.`);
        }
        const html = await respuesta.text();
        contenedor.innerHTML = html;

        // Inicialización específica del módulo cargado
        if (nombreVista === 'usuarios') {
            listarUsuarios();
        }
    } catch (err) {
        console.error("Error al cargar módulo:", err);
        contenedor.innerHTML = `
            <div class="alert alert-danger shadow-sm my-4 text-center">
                <i class="bi bi-exclamation-triangle-fill me-2 fs-4"></i>
                <div><strong>Error al cargar la vista:</strong> ${err.message}</div>
            </div>
        `;
    }
}

function actualizarInterfazSesion() {
    const menuModulos = document.getElementById('menuModulos');
    const panelUsuario = document.getElementById('panelUsuarioLogueado');
    const panelSinLogin = document.getElementById('panelSinLogin');
    const usuarioNombreDisplay = document.getElementById('usuarioNombreDisplay');
    const usuarioAliasDisplay = document.getElementById('usuarioAliasDisplay');
    const usuarioAvatar = document.getElementById('usuarioAvatar');

    if (usuarioAutenticado) {
        // Sesión iniciada
        if (menuModulos) menuModulos.classList.remove('d-none');
        if (panelUsuario) {
            panelUsuario.classList.remove('d-none');
            panelUsuario.classList.add('d-flex');
        }
        if (panelSinLogin) panelSinLogin.classList.add('d-none');

        if (usuarioNombreDisplay) usuarioNombreDisplay.textContent = usuarioAutenticado.nombre || 'Usuario';
        if (usuarioAliasDisplay) usuarioAliasDisplay.textContent = `@${usuarioAutenticado.usuario || ''}`;
        if (usuarioAvatar) {
            const inicial = (usuarioAutenticado.nombre || usuarioAutenticado.usuario || 'U').charAt(0).toUpperCase();
            usuarioAvatar.textContent = inicial;
        }
    } else {
        // Sin sesión
        if (menuModulos) menuModulos.classList.add('d-none');
        if (panelUsuario) {
            panelUsuario.classList.add('d-none');
            panelUsuario.classList.remove('d-flex');
        }
        if (panelSinLogin) panelSinLogin.classList.remove('d-none');
    }
}

// --------------------------------------------------------------------------
// Lógica del Login (Requerimiento 5)
// --------------------------------------------------------------------------
async function iniciarSesion() {
    const txtUser = document.getElementById('txtUsuarioLogin');
    const txtPass = document.getElementById('txtClaveLogin');
    const alerta = document.getElementById('loginAlerta');
    const btnSubmit = document.getElementById('btnIniciarSesion');

    if (!txtUser || !txtPass) return;

    const usuario = txtUser.value.trim();
    const clave = txtPass.value.trim();

    if (!usuario || !clave) {
        mostrarAlerta(alerta, 'Por favor ingrese su usuario y contraseña.', 'danger');
        return;
    }

    // Estado cargando
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Validando credenciales...`;

    try {
        const respuesta = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify({
                modulo: 'login',
                usuario: usuario,
                clave: clave
            })
        });

        const datos = await respuesta.json();

        if (datos.msg === 'ok' && datos.usuario) {
            // Login exitoso: Guardar sesión
            usuarioAutenticado = datos.usuario;
            sessionStorage.setItem('ugb_usuario_sesion', JSON.stringify(usuarioAutenticado));
            actualizarInterfazSesion();

            // Mensaje de éxito y transición al módulo de usuarios
            mostrarAlerta(alerta, `¡Bienvenido, ${usuarioAutenticado.nombre}! Ingresando al sistema...`, 'success');
            setTimeout(() => {
                abrirModulo('usuarios');
            }, 600);
        } else {
            // Acceso denegado (Requerimiento 5)
            mostrarAlerta(alerta, datos.msg || 'Acceso denegado: El usuario o la clave no están registrados.', 'danger');
            txtPass.value = '';
            txtPass.focus();
        }
    } catch (err) {
        console.error("Error en login:", err);
        mostrarAlerta(alerta, `Error de conexión con el servidor: ${err.message}`, 'danger');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = `<i class="bi bi-box-arrow-in-right fs-5"></i><span>Ingresar al Sistema</span>`;
    }
}

function cerrarSesion() {
    if (!confirm('¿Desea cerrar la sesión actual?')) return;
    usuarioAutenticado = null;
    sessionStorage.removeItem('ugb_usuario_sesion');
    actualizarInterfazSesion();
    cargarVista('login');
}

function abrirModulo(modulo, evento) {
    if (evento) evento.preventDefault();

    // Proteger acceso: si no está logueado, forzar login
    if (!usuarioAutenticado && modulo !== 'login') {
        cargarVista('login');
        return;
    }

    cargarVista(modulo);
}

function navegarInicio(evento) {
    if (evento) evento.preventDefault();
    if (usuarioAutenticado) {
        abrirModulo('usuarios');
    } else {
        cargarVista('login');
    }
}


// ==========================================================================
// 2. FORMULARIO DE USUARIOS - REGISTRO Y RECOLECCIÓN (Requerimiento 2 y 3)
// Recoger datos del formulario en JS y enviarlos a Python para almacenamiento
// ==========================================================================

async function guardarUsuario() {
    const idUsuario = document.getElementById('idUsuario')?.value.trim() || '';
    const txtUser = document.getElementById('txtUsuario');
    const txtPass = document.getElementById('txtClave');
    const txtNombre = document.getElementById('txtNombre');
    const txtDir = document.getElementById('txtDireccion');
    const txtTel = document.getElementById('txtTelefono');
    const alerta = document.getElementById('usuarioAlerta');
    const btnGuardar = document.getElementById('btnGuardarUsuario');

    const usuario = txtUser?.value.trim() || '';
    const clave = txtPass?.value.trim() || '';
    const nombre = txtNombre?.value.trim() || '';
    const direccion = txtDir?.value.trim() || '';
    const telefono = txtTel?.value.trim() || '';

    // Validaciones
    if (!usuario || !nombre || !direccion || !telefono) {
        mostrarAlerta(alerta, 'Complete todos los campos obligatorios.', 'warning');
        return;
    }

    if (!idUsuario && !clave) {
        mostrarAlerta(alerta, 'La contraseña es obligatoria para nuevos usuarios.', 'warning');
        return;
    }

    const accion = idUsuario ? 'modificar' : 'nuevo';

    // Empaquetar datos para Python (Requerimiento 2)
    const payload = {
        modulo: 'usuario',
        accion: accion,
        idUsuario: idUsuario ? parseInt(idUsuario) : null,
        usuario: usuario,
        clave: clave,
        nombre: nombre,
        direccion: direccion,
        telefono: telefono
    };

    btnGuardar.disabled = true;
    const txtOriginal = document.getElementById('btnGuardarUsuarioTexto').textContent;
    document.getElementById('btnGuardarUsuarioTexto').textContent = 'Procesando...';

    try {
        // Envío a Python vía POST (Requerimiento 2)
        const respuesta = await fetch('/usuario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify(payload)
        });

        const resp = await respuesta.json();

        if (resp.msg === 'ok') {
            const mensajeExito = idUsuario
                ? `Usuario '${usuario}' modificado exitosamente en la base de datos.`
                : `Usuario '${usuario}' registrado exitosamente en la tabla usuarios_usss014225.`;

            mostrarAlerta(alerta, mensajeExito, 'success');
            limpiarFormUsuario();
            listarUsuarios();
        } else {
            mostrarAlerta(alerta, resp.msg || 'Error al procesar la solicitud en el servidor.', 'danger');
        }
    } catch (err) {
        console.error("Error al guardar usuario:", err);
        mostrarAlerta(alerta, `Error de conexión: ${err.message}`, 'danger');
    } finally {
        btnGuardar.disabled = false;
        document.getElementById('btnGuardarUsuarioTexto').textContent = txtOriginal;
    }
}

function limpiarFormUsuario() {
    document.getElementById('frmUsuario')?.reset();
    const idField = document.getElementById('idUsuario');
    if (idField) idField.value = '';

    const titulo = document.getElementById('formUsuarioTitulo');
    if (titulo) titulo.innerHTML = '<i class="bi bi-person-plus-fill text-primary me-2"></i>Registrar Nuevo Usuario';

    const btnTexto = document.getElementById('btnGuardarUsuarioTexto');
    if (btnTexto) btnTexto.textContent = 'Guardar Usuario';

    const btnGuardar = document.getElementById('btnGuardarUsuario');
    if (btnGuardar) {
        btnGuardar.className = 'btn btn-primary flex-fill d-flex align-items-center justify-content-center gap-1 shadow-sm';
    }

    const btnEliminar = document.getElementById('btnEliminarUsuario');
    if (btnEliminar) btnEliminar.classList.add('d-none');

    const badgeEstado = document.getElementById('badgeEstadoForm');
    if (badgeEstado) {
        badgeEstado.textContent = 'Nuevo';
        badgeEstado.className = 'badge bg-primary-subtle text-primary border border-primary-subtle';
    }

    const txtPass = document.getElementById('txtClave');
    if (txtPass) txtPass.required = true;

    const reqClave = document.getElementById('reqClave');
    if (reqClave) reqClave.textContent = '*';

    const helpClave = document.getElementById('helpClave');
    if (helpClave) helpClave.textContent = 'Máximo 35 caracteres.';

    const alerta = document.getElementById('usuarioAlerta');
    if (alerta) alerta.classList.add('d-none');
}


// ==========================================================================
// 3. BÚSQUEDA, EDICIÓN Y ELIMINACIÓN DE USUARIOS (Requerimiento 4)
// ==========================================================================

async function listarUsuarios(buscar = '') {
    const tbl = document.getElementById('tblUsuarios');
    const badgeTotal = document.getElementById('totalUsuariosBadge');
    if (!tbl) return;

    try {
        const respuesta = await fetch(`/usuarios?buscar=${encodeURIComponent(buscar)}`);
        if (!respuesta.ok) {
            throw new Error(`HTTP ${respuesta.status}`);
        }
        const datos = await respuesta.json();
        listaUsuariosMemoria = Array.isArray(datos) ? datos : [];

        if (badgeTotal) {
            badgeTotal.textContent = `${listaUsuariosMemoria.length} usuario${listaUsuariosMemoria.length === 1 ? '' : 's'}`;
        }

        if (listaUsuariosMemoria.length === 0) {
            tbl.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center py-4 text-muted">
                        <i class="bi bi-inbox fs-3 d-block mb-1 text-secondary"></i>
                        ${buscar ? 'No se encontraron usuarios con ese criterio de búsqueda.' : 'No hay usuarios registrados en la tabla.'}
                    </td>
                </tr>
            `;
            return;
        }

        let filasHtml = '';
        listaUsuariosMemoria.forEach(u => {
            const id = u.idUsuario;
            const usuarioStr = escaparHtml(u.usuario || '');
            const nombreStr = escaparHtml(u.nombre || '');
            const telefonoStr = escaparHtml(u.telefono || u['teléfono'] || '');
            const direccionStr = escaparHtml(u.direccion || u['dirección'] || '');

            // Serializar objeto para evento onclick
            const userJson = JSON.stringify(u).replace(/"/g, '&quot;');

            filasHtml += `
                <tr>
                    <td class="px-3 fw-bold text-secondary">#${id}</td>
                    <td>
                        <span class="badge bg-primary-subtle text-primary border border-primary-subtle fw-semibold">
                            ${usuarioStr}
                        </span>
                    </td>
                    <td class="fw-semibold text-dark">${nombreStr}</td>
                    <td>
                        <span class="text-muted"><i class="bi bi-telephone text-primary me-1"></i>${telefonoStr}</span>
                    </td>
                    <td class="text-truncate" style="max-width: 180px;" title="${direccionStr}">
                        <i class="bi bi-geo-alt text-secondary me-1"></i>${direccionStr}
                    </td>
                    <td class="text-center px-3">
                        <div class="btn-group btn-group-sm" role="group">
                            <button class="btn btn-outline-primary" onclick="seleccionarUsuario(${userJson})" title="Editar usuario">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="eliminarUsuario(${id}, '${usuarioStr}')" title="Eliminar usuario">
                                <i class="bi bi-trash3-fill"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });

        tbl.innerHTML = filasHtml;
    } catch (err) {
        console.error("Error al listar usuarios:", err);
        tbl.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-3 text-danger">
                    <i class="bi bi-exclamation-circle me-1"></i>
                    Error al consultar la base de datos MySQL: ${err.message}
                </td>
            </tr>
        `;
    }
}

function buscarUsuarios() {
    clearTimeout(temporizadorBusqueda);
    temporizadorBusqueda = setTimeout(() => {
        const input = document.getElementById('txtBuscarUsuario');
        const termino = input ? input.value.trim() : '';
        listarUsuarios(termino);
    }, 200);
}

function limpiarBusqueda() {
    const input = document.getElementById('txtBuscarUsuario');
    if (input) {
        input.value = '';
        listarUsuarios('');
    }
}

function seleccionarUsuario(u) {
    if (!u) return;

    document.getElementById('idUsuario').value = u.idUsuario;
    document.getElementById('txtUsuario').value = u.usuario || '';
    document.getElementById('txtClave').value = u.clave || '';
    document.getElementById('txtNombre').value = u.nombre || '';
    document.getElementById('txtDireccion').value = u.direccion || u['dirección'] || '';
    document.getElementById('txtTelefono').value = u.telefono || u['teléfono'] || '';

    // Cambiar UI a modo edición
    const titulo = document.getElementById('formUsuarioTitulo');
    if (titulo) titulo.innerHTML = `<i class="bi bi-pencil-square text-warning me-2"></i>Modificar Usuario: <span class="text-primary">${escaparHtml(u.usuario)}</span>`;

    const btnTexto = document.getElementById('btnGuardarUsuarioTexto');
    if (btnTexto) btnTexto.textContent = 'Actualizar Cambios';

    const btnGuardar = document.getElementById('btnGuardarUsuario');
    if (btnGuardar) {
        btnGuardar.className = 'btn btn-warning flex-fill d-flex align-items-center justify-content-center gap-1 shadow-sm text-dark fw-semibold';
    }

    const btnEliminar = document.getElementById('btnEliminarUsuario');
    if (btnEliminar) btnEliminar.classList.remove('d-none');

    const badgeEstado = document.getElementById('badgeEstadoForm');
    if (badgeEstado) {
        badgeEstado.textContent = `Editando ID #${u.idUsuario}`;
        badgeEstado.className = 'badge bg-warning-subtle text-dark border border-warning-subtle';
    }

    const txtPass = document.getElementById('txtClave');
    if (txtPass) txtPass.required = false;

    const reqClave = document.getElementById('reqClave');
    if (reqClave) reqClave.textContent = '';

    const helpClave = document.getElementById('helpClave');
    if (helpClave) helpClave.textContent = 'Opcional. Si lo deja en blanco se conserva la clave actual.';

    // Scroll suave hacia el formulario en pantallas pequeñas
    document.getElementById('frmUsuario')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function eliminarUsuario(idUsuario, nombreUsuario) {
    if (!confirm(`¿Está seguro de eliminar al usuario '${nombreUsuario}' (ID: ${idUsuario})?\nEsta acción no se puede deshacer.`)) {
        return;
    }

    try {
        const respuesta = await fetch('/usuario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json; charset=utf-8' },
            body: JSON.stringify({
                modulo: 'usuario',
                accion: 'eliminar',
                idUsuario: idUsuario
            })
        });

        const resp = await respuesta.json();

        if (resp.msg === 'ok') {
            const alerta = document.getElementById('usuarioAlerta');
            mostrarAlerta(alerta, `Usuario '${nombreUsuario}' eliminado exitosamente.`, 'info');

            // Si el usuario eliminado era el que estaba en edición en el form, limpiar
            const idActualForm = document.getElementById('idUsuario')?.value;
            if (idActualForm == idUsuario) {
                limpiarFormUsuario();
            }

            listarUsuarios();
        } else {
            alert(`Error al eliminar usuario: ${resp.msg}`);
        }
    } catch (err) {
        console.error("Error al eliminar usuario:", err);
        alert(`Error de red al eliminar usuario: ${err.message}`);
    }
}

function eliminarUsuarioActual() {
    const id = document.getElementById('idUsuario')?.value;
    const usr = document.getElementById('txtUsuario')?.value || 'seleccionado';
    if (id) {
        eliminarUsuario(parseInt(id), usr);
    }
}


// ==========================================================================
// 4. UTILIDADES Y FORMATO
// ==========================================================================

function formatearTelefono(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length > 8) valor = valor.substring(0, 8);
    if (valor.length > 4) {
        valor = valor.substring(0, 4) + '-' + valor.substring(4);
    }
    input.value = valor;
}

function alternarVerClave(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'bi bi-eye';
    }
}

function mostrarAlerta(elementoAlerta, mensaje, tipo = 'info') {
    if (!elementoAlerta) return;
    elementoAlerta.className = `alert alert-${tipo} py-2 px-3 small border-0 shadow-sm animate-fade-in`;
    elementoAlerta.innerHTML = `<i class="bi bi-info-circle-fill me-1"></i> ${mensaje}`;
    elementoAlerta.classList.remove('d-none');
}

function escaparHtml(cadena) {
    return String(cadena)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}


// ==========================================================================
// 5. INICIALIZACIÓN DE LA APLICACIÓN
// Requerimiento 5: "El login debe de ser el primero que se muestre al ejecutar el servidor"
// ==========================================================================
window.addEventListener('DOMContentLoaded', () => {
    // Al ejecutar el servidor, cargamos la vista login en primer lugar
    usuarioAutenticado = null;
    sessionStorage.removeItem('ugb_usuario_sesion');
    actualizarInterfazSesion();
    cargarVista('login');
});
