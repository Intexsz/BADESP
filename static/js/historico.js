document.addEventListener('DOMContentLoaded', function () {
    // ===== PAGINAÇÃO SEGURA =====
    const totalPages = parseInt(document.body.getAttribute('data-total-pages')) || 1;
    const url = new URL(window.location.href);
    let page = parseInt(url.searchParams.get('page')) || 1;

    if (page < 1) page = 1;
    else if (page > totalPages) page = totalPages;

    if (parseInt(url.searchParams.get('page')) !== page) {
        url.searchParams.set('page', page);
        window.location.replace(url); // redireciona para a URL corrigida
    }

    // ===== SELETORES =====
    const btnMenu = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const linkLogout = document.getElementById("linkLogout");
    const selectFiltro = document.getElementById("selectFiltro");
    const formFiltro = document.getElementById("formFiltro");
    const linhasDenuncia = document.querySelectorAll(".linha-denuncia");

    // ===== MENU LATERAL (SIDEBAR) =====
    if (btnMenu && sidebar) {
        btnMenu.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('ativo');
        });

        // Fechar menu clicando fora
        document.addEventListener("click", (e) => {
            const clicouFora = !sidebar.contains(e.target) && !btnMenu.contains(e.target);
            if (sidebar.classList.contains("ativo") && clicouFora) {
                sidebar.classList.remove("ativo");
            }
        });
    }

    // ===== SUBMIT AUTOMÁTICO DO FILTRO (Substitui o onchange) =====
    if (selectFiltro && formFiltro) {
        selectFiltro.addEventListener('change', function () {
            formFiltro.submit();
        });
    }

    // ===== CLIQUE NAS LINHAS DA TABELA (Substitui o onclick) =====
    linhasDenuncia.forEach(linha => {
        linha.addEventListener('click', function () {
            const denunciaId = this.getAttribute('data-id');
            if (denunciaId) {
                verificarPin(denunciaId);
            }
        });
    });

    // ===== CONTROLE DE LOGOUT SEGURO =====
    if (linkLogout) {
        linkLogout.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            if (confirm("Deseja realmente sair?")) {
                window.location.href = "/Logout";
                alert("Logout realizado com sucesso!"); // Mantido do seu script original
            }
        });
    }

    // ===== FUNÇÃO PARA PROCESSAR O PIN / DETALHES =====
    async function verificarPin(denunciaId) {
        if (!confirmarAbrir()) return; // Validação preventiva local

        const form = document.createElement("form");
        form.method = "POST";
        form.action = `/allow_detail`;

        const inputIdzin = document.createElement("input");
        inputIdzin.type = "hidden";
        inputIdzin.name = "idzin";
        inputIdzin.value = denunciaId;

        form.appendChild(inputIdzin);
        document.body.appendChild(form);
        form.submit();
    }

    function confirmarAbrir() {
        return confirm("Você tem certeza que deseja abrir? Após aberto não poderá mais ser deletado e o usuario SABERÁ que foi você quem abriu");
    }
});
