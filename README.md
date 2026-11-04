# SOCKS5 Proxy Checker

Ferramenta em Python para **verificação paralela de proxies SOCKS5**, com validação de conectividade real, medição de latência, saída colorida no terminal e geração de relatórios em arquivo.

Ideal para testar listas de proxies obtidas de fontes públicas, validar pools internos ou auditar a saúde de um conjunto de servidores SOCKS5 antes de utilizá-los em automações, scrapers ou testes de segurança autorizados.

---

## ✨ Funcionalidades

- ⚡ **Verificação paralela** com `ThreadPoolExecutor` (workers configuráveis)
- 🌐 **Teste de conectividade real** — conecta a `8.8.8.8:53` através do proxy SOCKS5
- ⏱ **Medição de latência** em milissegundos para cada proxy
- 🎨 **Saída colorida** no terminal (verde = OK, amarelo = timeout, vermelho = falha)
- 📊 **Resumo estatístico** ao final (total, funcionando, timeout, falhas, erros de formato, tempo médio)
- 💾 **Exportação de resultados** para arquivo `.txt` com relatório completo
- 📁 **Duas formas de entrada** — digitação manual ou carregamento de arquivo
- 🛡 **Tratamento robusto de erros** — formato inválido, porta não numérica, timeouts, falhas de conexão

---

## 📦 Requisitos

```bash
pip install pysocks
