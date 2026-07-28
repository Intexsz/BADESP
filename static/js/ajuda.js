// Gerenciamento do Acordeão do FAQ
const faqs = document.querySelectorAll('#ajuda .faq');

faqs.forEach(faq => {
    faq.addEventListener('click', () => {
        // Fecha outras FAQs abertas
        faqs.forEach(f => {
            if (f !== faq) {
                f.classList.remove('active');
            }
        });
        // Alterna a FAQ clicada
        faq.classList.toggle('active');
    });
});

// Controle da Sidebar (Menu Lateral)
const btn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

if (btn && sidebar) {
    btn.addEventListener('click', (e) => {
        e.stopPropagation(); // Evita que o clique propague para o document
        sidebar.classList.toggle('ativo');
    });

    // Fechar menu clicando fora da sidebar
    document.addEventListener("click", (e) => {
        const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);
        if (sidebar.classList.contains("ativo") && clicouFora) {
            sidebar.classList.remove("ativo");
        }
    });
}

// Função Unificada de Logout
function confirmarLogout(e) {
    e.preventDefault();    // Bloqueia o redirecionamento padrão do HTML
    e.stopPropagation();   // Evita bolhas de eventos indesejadas

    if (confirm("Deseja realmente sair do sistema?")) {
        window.location.href = "/Logout";
    }
    return false;
}

// Vincula a função de logout globalmente para o HTML conseguir ler
window.confirmarLogout = confirmarLogout;
