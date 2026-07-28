document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const btnLogout = document.getElementById("btn-logout");
    const btnRecarregar = document.getElementById("btn-recarregar");

    // Controle do Menu Lateral (Sidebar)
    if (btn && sidebar) {
        btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));
    }

    // Função de Logout vinculada nativamente
    if (btnLogout) {
        btnLogout.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            if (confirm("Deseja realmente sair?")) {
                window.location.href = "/Logout";
            }
            return false;
        });
    }

    // Recarregar a página (Substitui o location.reload() inline)
    if (btnRecarregar) {
        btnRecarregar.addEventListener('click', () => {
            window.location.reload();
        });
    }

    // Fechar menu clicando fora da barra
    document.addEventListener("click", (e) => {
        if (sidebar && btn) {
            const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);

            if (sidebar.classList.contains("ativo") && clicouFora) {
                sidebar.classList.remove("ativo");
            }
        }
    });
});

window.addEventListener("pageshow", function () {
    // Garante que o modal feche caso a função exista no escopo global
    if (typeof fecharModal === "function") {
        fecharModal();
    }
});
