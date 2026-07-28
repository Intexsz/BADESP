document.addEventListener('DOMContentLoaded', () => {
    const btn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const btnLogout = document.getElementById("btn-logout");
    const inputAno = document.getElementById("input-ano");
    const inputTurma = document.getElementById("input-turma");

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

    // Função de Logout vinculada nativamente por ID
    if (btnLogout) {
        btnLogout.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm("Deseja realmente sair?")) {
                window.location.href = "/Logout";
            }
        });
    }

    // Filtro numérico para o campo Ano (Substitui o oninput inline)
    if (inputAno) {
        inputAno.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');
        });
    }

    // Forçar letras maiúsculas na Sigla da Turma
    if (inputTurma) {
        inputTurma.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase();
        });
    }
});
