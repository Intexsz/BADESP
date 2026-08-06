document.addEventListener("DOMContentLoaded", function () {
    // ==========================================
    // 1. INICIALIZAÇÃO DO VLIBRAS
    // ==========================================
    if (window.VLibras && window.VLibras.Widget) {
        new window.VLibras.Widget('https://vlibras.gov.br/app');
    }

    // ==========================================
    // 2. ELEMENTOS DO DOM
    // ==========================================
    const formCadastro = document.getElementById("form-cadastro");
    const selectSerie = document.getElementById("select-serie");
    const containerTurma = document.getElementById("container-turma");
    const selectTurma = document.getElementById("select-turma");
    const pinInput = document.getElementById("pin");
    const confirmarPinInput = document.getElementById("confirmar");
    const linkTermos = document.getElementById("link-termos");
    const termosHeader = document.getElementById("termosHeader");
    const termosBloco = document.getElementById("termosBloco");
    const termosIcon = document.getElementById("termosIcon");

    // ==========================================
    // 3. MÁSCARA APENAS NÚMEROS NOS INPUTS DE PIN
    // ==========================================
    function aplicarMascaraApenasNumeros(inputElement) {
        if (!inputElement) return;
        inputElement.addEventListener("input", function () {
            this.value = this.value.replace(/\D/g, "");
        });
    }

    aplicarMascaraApenasNumeros(pinInput);
    aplicarMascaraApenasNumeros(confirmarPinInput);

    // ==========================================
    // 4. FILTRO DE TURMAS (SE FOR ALUNO)
    // ==========================================
    if (selectSerie && containerTurma && selectTurma) {
        selectSerie.addEventListener("change", function () {
            const anoSelecionado = this.value;
            const optionsTurma = selectTurma.querySelectorAll("option");

            // Exibe o container da turma
            containerTurma.classList.remove("container-turma-escondido");
            containerTurma.style.display = "block";

            // Reseta a seleção
            selectTurma.value = "";

            // Filtra as opções visíveis
            optionsTurma.forEach(function (opt) {
                if (opt.value === "") {
                    opt.style.display = "block";
                } else if (opt.getAttribute("data-ano") === anoSelecionado) {
                    opt.style.display = "block";
                } else {
                    opt.style.display = "none";
                }
            });
        });
    }

    // ==========================================
    // 5. VALIDAÇÃO DO FORMULÁRIO (PIN)
    // ==========================================
    if (formCadastro) {
        formCadastro.addEventListener("submit", function (event) {
            const pinValue = pinInput ? pinInput.value : "";
            const confirmarValue = confirmarPinInput ? confirmarPinInput.value : "";

            if (pinValue === "000000" || pinValue === "0") {
                alert("O PIN não pode ser 000000!");
                event.preventDefault();
                return false;
            }

            if (pinValue !== confirmarValue) {
                alert("Os PINs não coincidem!");
                event.preventDefault();
                return false;
            }

            return true;
        });
    }

    // ==========================================
    // 6. TOGGLE DOS TERMOS E CONDIÇÕES
    // ==========================================
    function toggleTermos() {
        if (!termosBloco || !termosIcon) return;

        const estaEscondido = termosBloco.classList.contains("termos-escondido") ||
            termosBloco.style.display === "none";

        if (estaEscondido) {
            termosBloco.classList.remove("termos-escondido");
            termosBloco.style.display = "block";
            termosIcon.textContent = "▲";
        } else {
            termosBloco.classList.add("termos-escondido");
            termosBloco.style.display = "none";
            termosIcon.textContent = "▼";
        }
    }

    if (linkTermos) {
        linkTermos.addEventListener("click", function (e) {
            e.preventDefault();
            toggleTermos();
        });
    }

    if (termosHeader) {
        termosHeader.addEventListener("click", function () {
            toggleTermos();
        });
    }
});