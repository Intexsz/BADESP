function filtrarTurmas() {
    const anoSelecionado = document.getElementById("select-serie").value;
    const containerTurma = document.getElementById("container-turma");
    const selectTurma = document.getElementById("select-turma");
    const optionsTurma = selectTurma.querySelectorAll("option");

    // 1. Mostra o container da turma se um ano for escolhido
    containerTurma.style.display = 'block';

    // 2. Reseta o select de turma para a opção padrão
    selectTurma.value = "";

    // 3. Filtra os options baseado no data-ano
    let contagemValidos = 0;
    optionsTurma.forEach(opt => {
        if (opt.value === "") {
            opt.style.display = "block"; // Deixa o "Selecione a turma" visível
        } else if (opt.getAttribute("data-ano") === anoSelecionado) {
            opt.style.display = "block";
            contagemValidos++;
        } else {
            opt.style.display = "none";
        }
    });
}

function validarPin() {
    const pin = document.getElementById("pin").value;
    const confirmar = document.getElementById("confirmar").value;
    if (pin === '000000' || pin === '0') {
        alert("O PIN não pode ser 000000!");
        return false;
    }
    if (pin !== confirmar) {
        alert("Os PINs não coincidem!");
        return false;
    }
    return true;
}

function toggleTermos() {
    const termosBloco = document.getElementById("termosBloco");
    const termosIcon = document.querySelector(".termos-icon");
    if (termosBloco.style.display === "none") {
        termosBloco.style.display = "block";
        termosIcon.textContent = "▲";
    } else {
        termosBloco.style.display = "none";
        termosIcon.textContent = "▼";
    }
}
