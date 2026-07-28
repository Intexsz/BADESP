document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const btnLogout = document.getElementById("btn-logout");
    const containerDenuncias = document.querySelector('.denuncia');

    // Controle do Menu Lateral (Sidebar)
    if (btn && sidebar) {
        btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));
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

    // Gerenciamento de abertura das denúncias com mousedown (Evita duplo clique chato)
    if (containerDenuncias) {
        containerDenuncias.addEventListener('mousedown', (e) => {
            // Localiza o card mais próximo que foi clicado
            const card = e.target.closest('.denuncia-card');
            if (card) {
                e.preventDefault();
                const denunciaId = card.getAttribute('data-id');
                
                const confirmar = confirm(
                    "Você tem certeza que deseja abrir? Após aberto não poderá mais ser deletado e o aluno SABERÁ que foi você quem a abriu."
                );
                if (!confirmar) return;

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
        });
    }
});
