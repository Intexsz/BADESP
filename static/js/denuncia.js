// =========================================================================
// 1. CONFIGURAÇÃO GLOBAIS E ELEMENTOS BASE
// =========================================================================
const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");
const form = document.getElementById('form-denuncia');
const elemento = document.getElementById('botãooo');
const btn = document.querySelector('.menu-btn');
const sidebar = document.querySelector('.sidebar');

let resolverPrompt = null;
let aguardandoEnvio = false;

// =========================================================================
// 2. CAIXAS DE DIÁLOGO CUSTOMIZADAS (PROMPT MODAL)
// =========================================================================
// Use 'await caixaTexto("Qual seu nome?")' para substituir o 'prompt()' nativo
function caixaTexto(mensagem, valorPadrao = "") {
    return new Promise((resolve) => {
        const modal = document.getElementById("promptModal");
        const fundo = document.getElementById("fundoModal");
        const titulo = document.getElementById("promptMensagem");
        const input = document.getElementById("promptInput");

        if (titulo && input && fundo && modal) {
            titulo.textContent = mensagem;
            input.value = valorPadrao;
            fundo.style.display = "block";
            modal.style.display = "flex";
            input.focus();
        }
        resolverPrompt = resolve;
    });
}

function fecharPromptModal(confirmado) {
    const modal = document.getElementById("promptModal");
    const fundo = document.getElementById("fundoModal");
    const input = document.getElementById("promptInput");

    if (modal && fundo && input) {
        modal.style.display = "none";
        fundo.style.display = "none";

        if (resolverPrompt) {
            resolverPrompt(confirmado ? input.value : null);
            resolverPrompt = null;
        }
    }
}

// =========================================================================
// 3. LÓGICA DO MODAL PIN
// =========================================================================
function abrirModalPinEnvio() {
    aguardandoEnvio = true;
    const modal = document.getElementById("pinModal");
    const fundo = document.getElementById("fundoModal");
    const input = document.getElementById("pinInput");

    if (modal && fundo && input) {
        input.value = "";
        fundo.style.display = "block";
        modal.style.display = "flex";
        input.focus();
    }
}

function fecharModal() {
    const modal = document.getElementById("pinModal");
    const fundo = document.getElementById("fundoModal");
    const input = document.getElementById("pinInput");

    if (modal && fundo && input) {
        modal.style.display = "none";
        fundo.style.display = "none";
        input.value = "";
    }
}

async function confirmarPinModal() {
    const pinInput = document.getElementById("pinInput");
    if (!pinInput) return;

    const pin = pinInput.value;
    if (pin.length < 6) return alert("PIN incompleto");

    // CAPTURA SEGURO DO CSP: Obtém a URL gerada pelo Flask a partir do atributo do HTML
    const urlVerificarPin = form ? form.getAttribute("data-pin-url") : "/verificar_pin";

    try {
        const response = await fetch(urlVerificarPin, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            body: JSON.stringify({
                pin: pin
            })
        });

        const result = await response.json();

        if (result.status !== "ok") {
            return alert(result.mensagem || "PIN incorreto.");
        }

        fecharModal();

        if (aguardandoEnvio) {
            aguardandoEnvio = false;
            alert("Denúncia enviada com sucesso!");
            if (form) form.submit();
            if (elemento) elemento.remove();
        }

    } catch (error) {
        alert("Erro no servidor.");
    }
}

window.addEventListener("pageshow", fecharModal);

// =========================================================================
// 4. VALIDAÇÕES E SANITIZAÇÃO DE FORMULÁRIO
// =========================================================================
if (form) {
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        if (!validarFormularioCompleto()) {
            return;
        }

        const confirmado = confirm(
            "Você tem certeza que quer enviar esta denúncia? " +
            "A gestão escolar terá ACESSO ao seu nome e saberá que você enviou esta denúncia. " +
            "Após enviar, você não poderá mais editar. " +
            "Se enviar, só poderá APAGAR antes da Secretaria abrir sua denúncia. " +
            "Caso seja visualizada, você NÃO PODERÁ MAIS APAGAR SUA DENÚNCIA."
        );

        if (!confirmado) return;

        abrirModalPinEnvio();
    });
}

function sanitizarTexto(texto) {
    texto = texto.trim();
    const caracteresProibidos = /<|>|{|}|\||;|'|"|`|\\|\/\\|eval|script|onclick|onerror|onload/gi;
    texto = texto.replace(caracteresProibidos, '');
    texto = texto.replace(/\s+/g, ' ');
    return texto;
}

function validarCampoOutros(valor) {
    if (!valor || valor.trim().length === 0) return false;
    if (valor.length < 3) return false;
    const caracteresSuspeitos = /<script|javascript:|onerror|onclick|<\/|eval|alert|fetch|XMLHttpRequest/gi;
    if (caracteresSuspeitos.test(valor)) return false;
    return true;
}

function alternarCampoOutros() {
    const tipoSelect = document.getElementById('tipo');
    const containerOutros = document.getElementById('container-outros');
    const inputOutros = document.getElementById('outro-especificar');

    if (tipoSelect && containerOutros && inputOutros) {
        if (tipoSelect.value === 'Outros') {
            containerOutros.style.display = 'block';
            inputOutros.focus();
            inputOutros.setAttribute('required', 'required');
        } else {
            containerOutros.style.display = 'none';
            inputOutros.removeAttribute('required');
            inputOutros.value = '';
        }
    }
}

function validarFormularioCompleto() {
    const tipoSelect = document.getElementById('tipo');
    const inputOutros = document.getElementById('outro-especificar');

    if (tipoSelect && tipoSelect.value === 'Outros' && inputOutros) {
        const valor = inputOutros.value.trim();

        if (!valor) {
            alert('Por favor, especifique o tipo de ocorrência.');
            inputOutros.focus();
            return false;
        }

        if (!validarCampoOutros(valor)) {
            alert('O texto especificado é inválido. Verifique e tente novamente.');
            inputOutros.focus();
            return false;
        }
    }
    return true;
}

// =========================================================================
// 5. CARREGAMENTO DE DADOS DO SERVIDOR E PESSOAL GESTOR
// =========================================================================
const dadosElemento = document.getElementById('dados-servidor');
let professores = [];
let secretarias = [];

if (dadosElemento) {
    try {
        const dados = JSON.parse(dadosElemento.textContent);
        professores = dados.professores || [];
        secretarias = dados.secretarias || [];
    } catch (e) {
        console.error("Erro ao processar dados-servidor", e);
    }
}

function adicionarOpcao(select, valor, texto) {
    const opt = document.createElement('option');
    opt.value = valor;
    opt.textContent = texto;
    select.appendChild(opt);
}

function mostrarPessoas() {
    const quemElement = document.getElementById("quem");
    const pessoaDiv = document.getElementById("pessoaDiv");
    const pessoaSelect = document.getElementById("pessoa");

    if (!quemElement || !pessoaDiv || !pessoaSelect) return;

    const quem = quemElement.value;
    pessoaSelect.innerHTML = "";

    if (quem === "Professor") {
        pessoaDiv.style.display = "block";
        adicionarOpcao(pessoaSelect, "any", "Qualquer Professor");
        professores.forEach(nome => adicionarOpcao(pessoaSelect, nome, nome));
    }
    else if (quem === "Secretaria") {
        pessoaDiv.style.display = "block";
        // CORRIGIDO: mudado de 'select' para 'pessoaSelect'
        adicionarOpcao(pessoaSelect, "any", "Qualquer Gestão");
        secretarias.forEach(nome => adicionarOpcao(pessoaSelect, nome, nome));
    }
    else if (quem === "Ambos") {
        pessoaDiv.style.display = "none";
        adicionarOpcao(pessoaSelect, "any", "Qualquer Pessoa");
        professores.forEach(nome => adicionarOpcao(pessoaSelect, nome, nome));
        secretarias.forEach(nome => adicionarOpcao(pessoaSelect, nome, nome));
    }
    else {
        pessoaDiv.style.display = "none";
    }
}


function verificarSelect() {
    const select = document.getElementById("quem");
    if (select && select.value !== "") {
        mostrarPessoas();
    }
}
window.addEventListener("pageshow", () => setTimeout(verificarSelect, 50));
window.addEventListener("load", () => setTimeout(verificarSelect, 50));

// =========================================================================
// 6. GERENCIAMENTO DE ALUNOS E ENVOLVIDOS (DINÂMICO)
// =========================================================================
document.addEventListener('DOMContentLoaded', function () {
    const pinInput = document.getElementById("pinInput");
    const promptInput = document.getElementById("promptInput");
    const btnPinCancelar = document.getElementById("btn-pin-cancelar");
    const btnPinConfirmar = document.getElementById("btn-pin-confirmar");
    const btnPromptCancelar = document.getElementById("btn-prompt-cancelar");
    const btnPromptConfirmar = document.getElementById("btn-prompt-confirmar");
    const btnLogout = document.getElementById("btn-logout");

    // Validação numérica em tempo real no input de PIN substituindo o oninput inline
    if (pinInput) {
        pinInput.addEventListener('input', function (e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
        });
        pinInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                confirmarPinModal();
            }
        });
    }

    // Interceptador da tecla Enter no modal de Prompt customizado
    if (promptInput) {
        promptInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                fecharPromptModal(true);
            }
        });
    }

    // Vinculação dos cliques dos botões de controle dos Modals
    if (btnPinCancelar) btnPinCancelar.addEventListener('click', fecharModal);
    if (btnPinConfirmar) btnPinConfirmar.addEventListener('click', confirmarPinModal);
    if (btnPromptCancelar) btnPromptCancelar.addEventListener('mousedown', () => fecharPromptModal(false));
    if (btnPromptConfirmar) btnPromptConfirmar.addEventListener('mousedown', () => fecharPromptModal(true));
    if (btnLogout) btnLogout.addEventListener('click', confirmarLogout);
    // CAPTURA SEGURO DO CSP: Lê a listagem sem injetar chaves brutas no JS
    const dadosTurmaElemento = document.getElementById('dados-turmas');
    let alunosPorTurma = {};

    if (dadosTurmaElemento) {
        try {
            alunosPorTurma = JSON.parse(dadosTurmaElemento.textContent);
        } catch (e) {
            console.error("Erro ao analisar dados-turmas JSON", e);
        }
    }

    const selectTurma = document.getElementById("select-turma");
    const selectAluno = document.getElementById("select-aluno");
    const containerAluno = document.getElementById("container-aluno");
    const btnAdd = document.getElementById("btn-add-aluno");
    const listaContainer = document.getElementById("lista-envolvidos-container");
    const inputHidden = document.getElementById("input-envolvidos-final");
    const avisoVazio = document.getElementById("aviso-vazio");
    let listaEnvolvidos = [];

    const inputOutros = document.getElementById('outro-especificar');
    const mainCategorySelect = document.getElementById('tipo');
    const quemSelect = document.getElementById("quem");

    // Ativa listeners de sanitização
    if (inputOutros) {
        inputOutros.addEventListener('input', function (e) {
            e.target.value = sanitizarTexto(e.target.value);
        });

        inputOutros.addEventListener('blur', function (e) {
            const valor = e.target.value;
            if (valor && !validarCampoOutros(valor)) {
                alert('Por favor, insira um texto válido com pelo menos 3 caracteres.');
                e.target.value = '';
                e.target.focus();
            }
        });
    }

    if (mainCategorySelect) {
        mainCategorySelect.addEventListener('change', alternarCampoOutros);
    }

    if (quemSelect) {
        quemSelect.addEventListener('change', mostrarPessoas);
    }

    if (btn && sidebar) {
        btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));
    }

    if (!selectTurma || !selectAluno || !btnAdd || !listaContainer || !inputHidden) return;

    function atualizarSelectAlunos() {
        const turmaSelecionada = selectTurma.value;
        selectAluno.innerHTML = '<option value="" disabled selected>Selecione um aluno</option>';

        if (turmaSelecionada && alunosPorTurma[turmaSelecionada] && listaEnvolvidos.length < 5) {
            alunosPorTurma[turmaSelecionada].forEach(aluno => {
                if (!aluno) return;
                const option = document.createElement("option");
                option.value = aluno;
                option.textContent = aluno;
                selectAluno.appendChild(option);
            });
            if (containerAluno) containerAluno.style.display = "flex";
        } else {
            if (containerAluno) containerAluno.style.display = "none";
        }
    }

    function renderizarLista() {
        listaContainer.innerHTML = '';

        if (listaEnvolvidos.length === 0) {
            if (avisoVazio) {
                listaContainer.appendChild(avisoVazio);
                avisoVazio.style.display = 'block';
            }
        } else {
            if (avisoVazio) avisoVazio.style.display = 'none';
            listaEnvolvidos.forEach((item, index) => {
                const div = document.createElement('div');
                div.className = 'item-envolvido';
                // CORRIGIDO: Inseridas as crases corretas para a string HTML funcionar
                div.innerHTML = `<span><strong>${item.nome}</strong> <small>(${item.turma})</small></span> 
                             <button type="button" class="btn-remove" onclick="removerEnvolvido(${index})">&times;</button>`;
                listaContainer.appendChild(div);
            });
        }

        // CORRIGIDO: Inseridas as crases corretas para a interpolação de texto
        const textoFinal = listaEnvolvidos.map(i => `${i.nome} (${i.turma})`).join(', ');
        inputHidden.value = textoFinal;

        if (listaEnvolvidos.length >= 5) {
            if (containerAluno) containerAluno.style.display = "none";
            selectTurma.disabled = true;
            alert("Limite máximo de 5 envolvidos atingido.");
        } else {
            selectTurma.disabled = false;
            if (selectTurma.value && containerAluno) {
                containerAluno.style.display = "flex";
            }
        }
    }

    btnAdd.addEventListener('click', function () {
        const nome = selectAluno.value;
        const turma = selectTurma.value;

        if (!nome || !turma) {
            alert("Selecione uma turma e um aluno.");
            return;
        }

        const jaExiste = listaEnvolvidos.some(i => i.nome === nome && i.turma === turma);
        if (jaExiste) {
            alert("Este aluno já foi adicionado.");
            return;
        }

        listaEnvolvidos.push({ nome: nome, turma: turma });
        selectAluno.value = "";
        renderizarLista();
    });

    // Registra a remoção no escopo global (window)
    window.removerEnvolvido = function (index) {
        listaEnvolvidos.splice(index, 1);
        renderizarLista();
        atualizarSelectAlunos();
    };

    selectTurma.addEventListener('change', atualizarSelectAlunos);
    atualizarSelectAlunos();
});

// =========================================================================
// 7. SEGURANÇA E MENUS LATERAIS
// =========================================================================
function confirmarLogout(e) {
    e.preventDefault();
    e.stopPropagation();
    if (confirm("Deseja realmente sair?")) {
        window.location.href = "/Logout";
    }
    return false;
}
window.confirmarLogout = confirmarLogout;

document.addEventListener("click", (e) => {
    if (sidebar && btn) {
        const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);
        if (sidebar.classList.contains("ativo") && clicouFora) {
            sidebar.classList.remove("ativo");
        }
    }
});
