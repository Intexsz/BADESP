
      const btn = document.querySelector('.menu-btn');
      const sidebar = document.querySelector('.sidebar');

      btn.addEventListener('click', () => sidebar.classList.toggle('ativo'));

      function confirmarLogout(e) {
        e.preventDefault();          // trava o link
        e.stopPropagation();        // trava qualquer outro evento

        if (confirm("Deseja realmente sair?")) {
          window.location.href = "/Logout";
        }

        return false;
      }

      // ===== FECHAR MENU CLICANDO FORA + REDIRECIONAR P/ INÍCIO =====
      document.addEventListener("click", (e) => {
        const clicouFora = !sidebar.contains(e.target) && !btn.contains(e.target);

        if (sidebar.classList.contains("ativo") && clicouFora) {
          sidebar.classList.remove("ativo");
        }
      });

      function atualizarSeries(selectAno) {
        // 1. Achar a linha (tr) onde o clique aconteceu
        const linha = selectAno.closest('tr');

        // 2. Achar o select de série desta mesma linha
        const selectSerie = linha.querySelector('.select-serie');
        const anoSelecionado = selectAno.value;

        // 3. Pegar todas as opções de série
        const options = selectSerie.querySelectorAll('option');

        let encontrou = false;

        options.forEach(opt => {
          // O "Atual" a gente sempre deixa ou remove se quiser resetar
          if (opt.textContent.includes("(Atual)")) {
            opt.style.display = "block";
            return;
          }

          // Se o dado do ano bater com o selecionado, mostra
          if (opt.getAttribute('data-ano') === anoSelecionado) {
            opt.style.display = "block";
            encontrou = true;
          } else {
            opt.style.display = "none";
          }
        });

        // Resetar o valor do select de série para a primeira opção visível
        selectSerie.value = selectSerie.querySelector('option[style*="display: block"]').value;
      }