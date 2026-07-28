document.addEventListener('DOMContentLoaded', function () {
    const btn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const linkLogout = document.getElementById("linkLogout");

    // ===== SELETORES DOS FORMULÁRIOS DA SECRETARIA =====
    const formAbrir = document.querySelector('.form-confirmar-abrir');
    const formRecusar = document.querySelector('.form-confirmar-recusar');
    const formArquivar = document.querySelector('.form-confirma-arquivar');
    const formTexto = document.querySelector('.form-confirmar-texto');

    // ===== VINCULAÇÃO DAS CONFIRMAÇÕES (Substitui o onclick inline) =====
    if (formAbrir) {
        formAbrir.addEventListener('submit', function (e) {
            if (!confirmarAbrir()) e.preventDefault();
        });
    }

    if (formRecusar) {
        formRecusar.addEventListener('submit', function (e) {
            if (!confirmarRecusar()) e.preventDefault();
        });
    }

    if (formArquivar) {
        formArquivar.addEventListener('submit', function (e) {
            if (!confirmaArquivar()) e.preventDefault();
        });
    }

    if (formTexto) {
        formTexto.addEventListener('submit', function (e) {
            if (!confirmarTexto()) e.preventDefault();
        });
    }

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

    // ===== CONTROLE DE LOGOUT SEGURO VIA EVENT LISTENER =====
    if (linkLogout) {
        linkLogout.addEventListener('click', function (e) {
            confirmarLogout(e);
        });
    }
});

// ===== FUNÇÕES DE CONFIRMAÇÃO GLOBAIS =====
function confirmarAbrir() {
    return confirm("Deseja aprovar esta denúncia?");
}

function confirmaArquivar() {
    return confirm("Deseja arquivar esta denúncia?");
}

function confirmarRecusar() {
    return confirm("Deseja recusar esta denúncia?");
}

function confirmarTexto() {
    return confirm("Deseja enviar um comentário? Você só pode comentar uma vez.");
}

function confirmarLogout(e) {
    e.preventDefault();          // trava o link
    e.stopPropagation();        // trava qualquer outro evento

    if (confirm("Deseja deslogar?")) {
        window.location.href = "/Logout";
    }

    return false;
}
