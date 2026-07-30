const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");

document.addEventListener('DOMContentLoaded', function () {
    const btn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const pinInput = document.getElementById("pinInput");
    const btnCancelarPin = document.getElementById("btnCancelarPin");
    const btnConfirmarPin = document.getElementById("btnConfirmarPin");
    const fundoModalPin = document.getElementById("fundoModalPin");
    const linkLogout = document.getElementById("linkLogout");

    // Captura todos os cards de link dinamicamente
    const cards = document.querySelectorAll(".dashboard-container .card");

    // Variável que guarda qual card foi clicado
    let valorAtual = "";

    // ===== MENU LATERAL (SIDEBAR) =====
    if (btn && sidebar) {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('ativo');
        });

        // Fechar menu clicando fora
        document.addEventListener("click", (e) => {
            const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);
            if (sidebar.classList.contains("ativo") && clicouFora) {
                sidebar.classList.remove("ativo");
            }
        });
    }

    // ===== TRATAMENTO DOS INPUTS (Substitui o oninput inline) =====
    if (pinInput) {
        pinInput.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 6);
        });

        // Permite Enter no input
        pinInput.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                confirmarPinModal();
            }
        });
    }

    // ===== CAPTURA DOS CLIQUES NOS CARDS =====
    cards.forEach(card => {
        card.addEventListener('click', function (e) {
            e.preventDefault();
            const rota = this.getAttribute('data-origem'); // Se precisar usar a rota futuramente
            const valor = this.getAttribute('data-destino');
            verificarPin(rota, valor);
        });
    });

    // ===== EVENTOS DOS BOTÕES DO MODAL (Substitui onmousedown inline) =====
    if (btnCancelarPin) {
        btnCancelarPin.addEventListener('mousedown', fecharModalPin);
    }

    if (btnConfirmarPin) {
        btnConfirmarPin.addEventListener('mousedown', confirmarPinModal);
    }

    if (fundoModalPin) {
        fundoModalPin.addEventListener("click", fecharModalPin);
    }

    // ===== EVENTO DE LOGOUT SEGURO =====
    if (linkLogout) {
        linkLogout.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (confirm("Deseja realmente sair?")) {
                window.location.href = "/Logout";
            }
        });
    }

    // ===== FUNÇÕES DO MODAL =====

    // Abre o modal
    function verificarPin(rota, valor) {
        valorAtual = valor;

        const modal = document.getElementById("modalPin");
        const fundo = document.getElementById("fundoModalPin");
        const input = document.getElementById("pinInput");

        if (fundo && modal && input) {
            fundo.style.display = "block";
            modal.classList.add("ativo");
            input.value = "";
            input.focus();
        }
    }

    // Fecha o modal
    function fecharModalPin() {
        const modal = document.getElementById("modalPin");
        const fundo = document.getElementById("fundoModalPin");
        const input = document.getElementById("pinInput");

        if (modal) modal.classList.remove("ativo");
        if (fundo) fundo.style.display = "none";
        if (input) input.value = "";
    }

    // Confirma o PIN via Fetch API
    async function confirmarPinModal() {
        const inputPin = document.getElementById("pinInput");
        if (!inputPin) return;

        const pin = inputPin.value.trim();

        if (pin === "") {
            alert("Digite o PIN.");
            inputPin.focus();
            return;
        }

        try {
            // Alterado de Jinja para a URL literal da sua rota do Flask
            const response = await fetch("/verificar_pin", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ pin: pin })
            });

            const result = await response.json();

            if (result.status === "ok") {
                fecharModalPin();

                const form = document.createElement("form");
                form.method = "POST";
                form.action = "/allow_folder";

                const csrf = document.createElement("input");
                csrf.type = "hidden";
                csrf.name = "csrf_token";
                csrf.value = csrfToken;
                form.appendChild(csrf);

                const input = document.createElement("input");
                input.type = "hidden";
                input.name = "nome";
                input.value = valorAtual;

                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            } else {
                alert(result.mensagem || "PIN incorreto.");
                inputPin.value = "";
                inputPin.focus();
            }

        } catch (erro) {
            console.error("Erro:", erro);
            alert("Erro ao verificar o PIN.");
        }
    }
});
