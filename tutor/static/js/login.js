const form = document.getElementById("form-login");
const erro = document.getElementById("erro");

form.addEventListener("submit", (e) => {
  // Impede o envio do formulário antes da validação
  e.preventDefault();
  
  const email = form.email.value.trim();
  const senha = form.senha.value;

  if (!email || !/^\S+@\S+\.\S+$/.test(email)) {
    erro.textContent = "Digite um e-mail válido.";
    form.email.focus();
    return;
  }
  if (senha.length < 8) {
    erro.textContent = "A senha precisa ter pelo menos 8 caracteres.";
    form.senha.focus();
    return;
  }

  erro.textContent = "";
  // console.log("Login enviado para:", email);
  
  // Para que o Django processe o formulário após a validação JS, 
  // foi comentado o console.log acima e adicionado a linha abaixo:
  form.submit();
});