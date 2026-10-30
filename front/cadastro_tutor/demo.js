// DEMONSTRAÇÃO: simula o banco de dados com localStorage.
// O back substitui estas funções por chamadas ao servidor/MySQL. APAGAR depois.
const Demo = {
  listar() {
    try {
      const t = JSON.parse(localStorage.getItem("tutores"));
      if (Array.isArray(t)) return t;
    } catch (e) {}
    const inicial = [{
      id: 1, nome: "Thais Souza", email: "thaisssss@alunos.utfpr.edu.br",
      telefone: "(44) 99999-9999", senha: "12345678"
    }];
    localStorage.setItem("tutores", JSON.stringify(inicial));
    return inicial;
  },
  salvarTodos(lista) { localStorage.setItem("tutores", JSON.stringify(lista)); },
  emailExiste(email, ignorarId) {
    return this.listar().some(t => t.id !== ignorarId && t.email.toLowerCase() === email.toLowerCase());
  },
  adicionar(dados) {
    const lista = this.listar();
    const id = lista.reduce((m, t) => Math.max(m, t.id), 0) + 1;
    lista.push({ id, ...dados });
    this.salvarTodos(lista);
  },
  atualizar(id, dados) {
    const lista = this.listar();
    const t = lista.find(x => x.id === id);
    if (!t) return;
    t.nome = dados.nome; t.email = dados.email; t.telefone = dados.telefone;
    if (dados.senha) t.senha = dados.senha;   // senha vazia = mantém a atual
    this.salvarTodos(lista);
  },
  excluir(id) { this.salvarTodos(this.listar().filter(t => t.id !== id)); }
};