const formulario = document.querySelector(".chat-form");
const campoMensaje = document.querySelector('textarea[name="mensaje"]');
const contenedorMensajes = document.querySelector(".messages");

formulario.addEventListener("submit", async function (evento) {
    evento.preventDefault();

    const texto = campoMensaje.value.trim();

    if (!texto) {
        return;
    }

    agregarMensajeTecnico(texto);

    campoMensaje.value = "";

    const loader = agregarLoaderLozAI();

    const datos = new FormData(formulario);
    datos.set("mensaje", texto);

    try {
        const respuesta = await fetch(
            formulario.dataset.url,
            {
                method: "POST",
                body: datos
            }
        );

        const resultado = await respuesta.json();

        loader.remove();

        if (!respuesta.ok) {
            agregarMensajeLozAI(
                resultado.error || "Ocurrió un error."
            );
            return;
        }

        agregarMensajeLozAI(
            resultado.respuesta,
            resultado.fecha
        );

    } catch (error) {
        loader.remove();

        agregarMensajeLozAI(
            "No se pudo comunicar con LozAI."
        );
    }
});

campoMensaje.addEventListener("keydown", function (evento) {

    if (evento.key === "Enter" && !evento.shiftKey) {
        evento.preventDefault();

        formulario.requestSubmit();
    }
});

function agregarMensajeTecnico(texto) {
    eliminarChatVacio();

    const mensaje = document.createElement("div");

    mensaje.className = "message message-user";

    mensaje.innerHTML = `
        <strong>Tecnico</strong>
        <p>${escaparHTML(texto)}</p>
        <small>Ahora</small>
    `;

    contenedorMensajes.appendChild(mensaje);

    moverChatAlFinal();
}

function agregarMensajeLozAI(texto, fecha = "Ahora") {
    const mensaje = document.createElement("div");

    mensaje.className = "message message-ai";

    mensaje.innerHTML = `
        <strong>LozAI</strong>
        <p>${escaparHTML(texto).replace(/\n/g, "<br>")}</p>
        <small>${fecha}</small>
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
    contenedorMensajes.scrollTop =
        contenedorMensajes.scrollHeight;
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

