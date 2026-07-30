let denunciaAtual = null;
const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");

// Controle do Menu Lateral (Sidebar)
const btn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

function abrirModalPin(id) {
    denunciaAtual = id;
    const fundo = document.getElementById("fundoModal");
    const modal = document.getElementById("pinModal");
    const input = document.getElementById("pinInput");

    if (fundo && modal && input) {
        input.value = "";
        fundo.style.display = "block";
        modal.classList.add("ativo");
        modal.style.display = "flex"; // Garante que o modal mude o display para aparecer
        input.focus();
    }
}
window.abrirModalPin = abrirModalPin;

function fecharModal() {
    const fundo = document.getElementById("fundoModal");
    const modal = document.getElementById("pinModal");
    const input = document.getElementById("pinInput");

    if (fundo && modal && input) {
        fundo.style.display = "none";
        modal.classList.remove("ativo");
        modal.style.display = "none";
        input.value = "";
    }
}

async function confirmarPinModal() {
    const input = document.getElementById("pinInput");
    const fundo = document.getElementById("fundoModal");

    if (!input || !fundo) return;

    const pin = input.value;
    if (pin.length < 6) return alert("PIN incompleto");

    const urlVerificarPin = fundo.getAttribute("data-pin-url") || "/verificar_pin";

    try {
        const response = await fetch(urlVerificarPin, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                pin: pin
            })
        });

        const result = await response.json();

        if (result.status === "ok") {
            fecharModal();

            const form = document.createElement("form");
            form.method = "POST";
            form.action = "/allow_detail";

            const csrf = document.createElement("input");
            csrf.type = "hidden";
            csrf.name = "csrf_token";
            csrf.value = csrfToken;
            form.appendChild(csrf);

            const inputId = document.createElement("input");
            inputId.type = "hidden";
            inputId.name = "idzin";
            inputId.value = denunciaAtual;

            form.appendChild(inputId);
            document.body.appendChild(form);
            form.submit();
        } else {
            alert(result.mensagem || "PIN incorreto.");
        }

    } catch (e) {
        alert("Erro no servidor.");
    }
}

function confirmarLogout(e) {
    e.preventDefault();
    e.stopPropagation();

    if (confirm("Deseja realmente sair?")) {
        window.location.href = "/Logout";
    }
    return false;
}

// Inicialização segura dos eventos após o DOM estar pronto
document.addEventListener('DOMContentLoaded', () => {
    const fundoModal = document.getElementById("fundoModal");
    const pinInput = document.getElementById("pinInput");
    const btnPinCancelar = document.getElementById("btn-pin-cancelar");
    const btnPinConfirmar = document.getElementById("btn-pin-confirmar");
    const btnLogout = document.getElementById("btn-logout");
    const filtroSelect = document.getElementById("filtro-select");
    const filtroForm = document.getElementById("filtro-form");
    const containerDenuncias = document.getElementById("denuncias-container");

    // SOLUÇÃO DO FILTRO: Captura a mudança do select e força o envio correto do formulário
    if (filtroSelect && filtroForm) {
        filtroSelect.addEventListener('change', () => {
            filtroForm.submit();
        });
    }

    // SOLUÇÃO DA ABERTURA: Captura cliques no contêiner de denúncias
    if (containerDenuncias) {
        containerDenuncias.addEventListener('click', (e) => {
            // Verifica se o elemento clicado possui a classe correta
            if (e.target.classList.contains('btn-abrir')) {
                const idDenuncia = e.target.getAttribute('data-id');
                if (idDenuncia) {
                    abrirModalPin(idDenuncia);
                }
            }
        });
    }

    if (fundoModal) {
        fundoModal.addEventListener("click", fecharModal);
    }

    if (pinInput) {
        pinInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
        });
        pinInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                confirmarPinModal();
            }
        });
    }

    // ALTERADO PARA MOUSEDOWN: Sincronizado perfeitamente com o denuncia.js
    if (btnPinCancelar) btnPinCancelar.addEventListener('mousedown', fecharModal);
    if (btnPinConfirmar) btnPinConfirmar.addEventListener('mousedown', confirmarPinModal);

    if (btnLogout) btnLogout.addEventListener('click', confirmarLogout);

    if (btn && sidebar) {
        btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));
    }
});

// Fechar menu clicando fora da barra
document.addEventListener("click", (e) => {
    if (sidebar && btn) {
        const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);
        if (sidebar.classList.contains("ativo") && clicouFora) {
            sidebar.classList.remove("ativo");
        }
    }
});

window.addEventListener("pageshow", function () {
    fecharModal();
});
