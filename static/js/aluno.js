let denunciaAtual = null;

const btn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

// =================== ABRIR / FECHAR SIDEBAR ===================
if (btn && sidebar) {
    btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));
}

// ===== FECHAR MENU CLICANDO FORA =====
document.addEventListener("click", (e) => {
    const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);
    if (sidebar.classList.contains("ativo") && clicouFora) {
        sidebar.classList.remove("ativo");
    }
});

// =================== LOGOUT ===================
const btnLogout = document.getElementById('btn-logout');
if (btnLogout) {
    btnLogout.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        if (confirm("Deseja realmente sair?")) {
            window.location.href = "/Logout";
        }
    });
}

// =================== AUTO SUBMIT DE FILTROS ===================
document.querySelectorAll('.auto-submit').forEach(select => {
    select.addEventListener('change', function () {
        this.form.submit();
    });
});

// =================== BOTÃO SALVAR TODAS ===================
const btnSalvarTodas = document.getElementById('btn-salvar-todas');
if (btnSalvarTodas) {
    btnSalvarTodas.addEventListener('click', () => {
        alert('Alterações feitas com sucesso!');
    });
}

// =================== ATUALIZAR SÉRIES PELA LINHA ===================
function atualizarSeries(selectAno) {
    // 1. Achar a linha (tr) onde o clique aconteceu
    const linha = selectAno.closest('tr');

    // 2. Achar o select de série desta mesma linha
    const selectSerie = linha.querySelector('.select-serie');
    const anoSelecionado = selectAno.value;

    // 3. Pegar todas as opções de série
    const options = selectSerie.querySelectorAll('option');

    options.forEach(opt => {
        // O "Atual" a gente sempre deixa
        if (opt.textContent.includes("(Atual)")) {
            opt.style.display = "block";
            return;
        }

        // Se o dado do ano bater com o selecionado, mostra
        if (opt.getAttribute('data-ano') === anoSelecionado) {
            opt.style.display = "block";
        } else {
            opt.style.display = "none";
        }
    });

    // Seleciona a primeira opção da lista que ficou visível após mudar o ano
    const primeiraOpcaoVisivel = selectSerie.querySelector('option[style*="display: block"]');
    if (primeiraOpcaoVisivel) {
        selectSerie.value = primeiraOpcaoVisivel.value;
    }
}

// Associa o evento change a todas as caixas de select de Ano na tabela
document.querySelectorAll(".select-ano").forEach(select => {
    select.addEventListener("change", function () {
        atualizarSeries(this);
    });
});

// =================== EVENTOS DE AÇÃO / TABELA ===================

// Evita que clicar dentro do "TD de Ações" acione o evento de clicar em toda a linha da tabela
document.querySelectorAll('.coluna-acoes').forEach(td => {
    td.addEventListener('click', function (e) {
        e.stopPropagation();
    });
});

// Gerencia as mensagens de confirmação dos botões "Reativar", "Remover Suspensão", "Encerrar", etc.
document.querySelectorAll('.btn-confirmar').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.stopPropagation();

        const mensagem = this.getAttribute('data-msg') || "Tem certeza que deseja continuar?";

        // Se o usuário clicar em Cancelar no popup, impede o envio do form
        if (!confirm(mensagem)) {
            e.preventDefault();
        }
    });
});

// Impede que clicar nos botões que são formato de link <a> feche ou acione a linha inteira da tabela
document.querySelectorAll('.btn-suspender').forEach(link => {
    link.addEventListener('click', function (e) {
        e.stopPropagation();
    });
});