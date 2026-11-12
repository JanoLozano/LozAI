const formulario = document.querySelector(".chat-form");
const campoMensaje = document.querySelector('textarea[name="mensaje"]');
const contenedorMensajes = document.querySelector(".messages");
const botonEnviar = formulario.querySelector('button[type="submit"]');

let procesando = false;

formulario.addEventListener("submit", async function (evento) {
    evento.preventDefault();

    if (procesando) return;

    const texto = campoMensaje.value.trim();

    if (!texto) return;

    procesando = true;
    botonEnviar.disabled = true;
    campoMensaje.disabled = true;

    agregarMensajeTecnico(texto);
    campoMensaje.value = "";

    const loader = agregarLoaderLozAI();

    const datos = new FormData(formulario);
    datos.set("mensaje", texto);

    try {
        const respuesta = await fetch(formulario.dataset.url, {
            method: "POST",
            body: datos
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            agregarMensajeSistema(
                resultado.error || "No se pudo procesar la solicitud."
            );
            return;
        }

        agregarMensajeLozAI(
            resultado.respuesta,
            resultado.fecha,
            resultado.proveedor
        );

    } catch (error) {
        agregarMensajeSistema(
            "No se pudo establecer comunicación con el servidor."
        );

    } finally {
        loader.remove();
        procesando = false;
        botonEnviar.disabled = false;
        campoMensaje.disabled = false;
        campoMensaje.focus();
    }
});

campoMensaje.addEventListener("keydown", function (evento) {
    if (evento.key === "Enter" && !evento.shiftKey) {
        evento.preventDefault();

        if (!procesando) {
            formulario.requestSubmit();
        }
    }
});

function agregarMensajeTecnico(texto) {
    eliminarChatVacio();

    const mensaje = document.createElement("div");
    mensaje.className = "message message-user";

    mensaje.innerHTML = `
        <strong>Técnico</strong>
        <p>${escaparHTML(texto)}</p>
        <small>Ahora</small>
    `;

    contenedorMensajes.appendChild(mensaje);
    moverChatAlFinal();
}


function agregarMensajeLozAI(texto, fecha = "Ahora", proveedor = null) {
    eliminarChatVacio();

    const mensaje = document.createElement("div");
    mensaje.className = "message message-ai";

    let informacionProveedor = "";

    if (proveedor) {
        informacionProveedor = `
            <span class="badge bg-secondary ms-2">
                ${escaparHTML(proveedor)}
            </span>
        `;
    }

    mensaje.innerHTML = `
        <strong>
            LozAI
            ${informacionProveedor}
        </strong>
        <p>${escaparHTML(texto).replace(/\n/g, "<br>")}</p>
        <small>${escaparHTML(fecha)}</small>
    `;

    contenedorMensajes.appendChild(mensaje);
    moverChatAlFinal();
}


function agregarMensajeSistema(texto) {
    eliminarChatVacio();

    const mensaje = document.createElement("div");
    mensaje.className = "alert alert-danger mt-2";
    mensaje.setAttribute("role", "alert");

    mensaje.innerHTML = `
        <strong><i class="bi bi-exclamation-triangle"></i> Sistema</strong>
        <p class="mb-0">${escaparHTML(texto)}</p>
    `;

    contenedorMensajes.appendChild(mensaje);
    moverChatAlFinal();
}

function agregarLoaderLozAI() {
    const loader = document.createElement("div");
    loader.className = "message message-ai message-loading";

    loader.innerHTML = `
        <strong>LozAI</strong>
        <p>Analizando...</p>
    `;

    contenedorMensajes.appendChild(loader);
    moverChatAlFinal();

    return loader;
}

function moverChatAlFinal() {
    contenedorMensajes.scrollTop = contenedorMensajes.scrollHeight;
}

function eliminarChatVacio() {
    const chatVacio = document.querySelector(".empty-chat");

    if (chatVacio) {
        chatVacio.remove();
    }
}

function escaparHTML(texto) {
    const elemento = document.createElement("div");
    elemento.textContent = texto;
    return elemento.innerHTML;
}
