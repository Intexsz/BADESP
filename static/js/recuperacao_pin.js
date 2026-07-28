document.addEventListener('DOMContentLoaded', function () {
    // ===== CONFIGURAÇÃO DE ALUNOS E TURMAS =====
    // Lemos a string do JSON direto do atributo do HTML e convertemos em Objeto JS
    const conteudoPrincipal = document.getElementById("conteudo-principal");
    let alunosPorTurma = {};

    if (conteudoPrincipal) {
        const dadosAtributo = conteudoPrincipal.getAttribute("data-alunos");
        try {
            alunosPorTurma = JSON.parse(dadosAtributo) || {};
        } catch (erro) {
            console.error("Erro ao processar os dados das turmas:", erro);
        }
    }

    const selectTurma = document.getElementById("select-turma");
    const selectAluno = document.getElementById("select-aluno");
    const containerAluno = document.getElementById("container-aluno");
    const form = document.getElementById("alterar-pin-form");
    const pinInput = document.getElementById("pin");
    const confirmarInput = document.getElementById("confirmar");
    const btn = document.querySelector('.menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const linkLogout = document.getElementById("linkLogout");

    function atualizarAlunos() {
        if (!selectTurma || !selectAluno || !containerAluno) return;

        const turmaSelecionada = selectTurma.value;
        selectAluno.innerHTML = '<option value="" disabled selected>Selecione um aluno</option>';

        if (turmaSelecionada && alunosPorTurma[turmaSelecionada]) {
            alunosPorTurma[turmaSelecionada].forEach(aluno => {
                if (!aluno) return;
                const option = document.createElement("option");
                option.value = aluno;
                option.textContent = aluno;
                selectAluno.appendChild(option);
            });
            containerAluno.style.display = "block";
        } else {
            containerAluno.style.display = "none";
        }
    }

    if (selectTurma) {
        selectTurma.addEventListener('change', atualizarAlunos);
        atualizarAlunos();
    }

    // ===== MÁSCARA NUMÉRICA COMPATÍVEL COM CSP =====
    function aplicarMascara(inputElement) {
        if (inputElement) {
            inputElement.addEventListener('input', function () {
                this.value = this.value.replace(/\D/g, '').slice(0, 6);
            });
        }
    }
    aplicarMascara(pinInput);
    aplicarMascara(confirmarInput);

    // ===== VALIDAÇÃO DO FORMULÁRIO =====
    function validarPin() {
        if (!pinInput || !confirmarInput) return true;

        const pin = pinInput.value;
        const confirmar = confirmarInput.value;

        if (pin !== confirmar) {
            alert("Os PINs não coincidem!");
            return false;
        }

        if (pin === "000000") {
            alert("PIN inválido! Não pode ser 000000.");
            return false;
        }

        return true;
    }

    if (form) {
        form.addEventListener('submit', function (event) {
            if (!validarPin()) {
                event.preventDefault();
            }
        });
    }

    // ===== MENU LATERAL (SIDEBAR) =====
    if (btn && sidebar) {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('ativo');
        });

        document.addEventListener("click", (e) => {
            const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);
            if (sidebar.classList.contains("ativo") && clicouFora) {
                sidebar.classList.remove("ativo");
            }
        });
    }

    // ===== CONTROLE DE LOGOUT SEGURO =====
    if (linkLogout) {
        linkLogout.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            if (confirm("Deseja realmente sair?")) {
                window.location.href = "/Logout";
            }
        });
    }
});
