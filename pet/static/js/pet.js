const form = document.getElementById("form-pet");
const status = document.getElementById("status");

// Atualizado para referenciar a ID correta da coleira no HTML
const coleira = document.getElementById("id_disp_rastreamento");
coleira.addEventListener("input", () => {
  coleira.value = coleira.value.replace(/^#+/, "");
});

document.getElementById("cancelar").addEventListener("click", () => {
  form.reset();
  status.textContent = "";
  if (history.length > 1) history.back();
});

// A validação via JS para limpar os espaços em branco foi mantida,
// mas o submit continuará fluindo para o Django salvar no banco.
form.addEventListener("submit", () => {
  const inputs = form.querySelectorAll("input, textarea");
  inputs.forEach((input) => {
    if (input.value) {
      input.value = input.value.trim();
    }
  });
});