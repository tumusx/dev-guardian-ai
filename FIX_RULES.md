# ⚠️ REGRAS ABSOLUTAS PARA CORREÇÃO

## LEIA ISTO PRIMEIRO - REGRAS QUE NÃO PODEM SER QUEBRADAS

### ❌ PROIBIDO (100% VEDADO)
- ❌ Adicionar novos métodos ou funções
- ❌ Adicionar novos campos ou propriedades
- ❌ Remover funções ou métodos existentes
- ❌ Alterar lógica que funciona
- ❌ Refatorar código
- ❌ Renomear variáveis ou funções
- ❌ Adicionar imports
- ❌ Mudar estrutura de classes
- ❌ Melhorar código
- ❌ Fazer qualquer coisa além de CORRIGIR O ERRO

### ✅ PERMITIDO (APENAS ISTO)
- ✅ Corrigir erros de sintaxe
- ✅ Corrigir erros de tipo
- ✅ Corrigir chamadas de função erradas
- ✅ Corrigir parênteses, colchetes, etc
- ✅ Corrigir typos em nomes
- ✅ NADA MAIS

## REGRA DE OURO

**SE NÃO CAUSA ERRO DIRETO, NÃO MUDE**

O arquivo DEVE ser o mínimo absolutamente necessário para compilar. Nada além disso.

## EXEMPLO CORRETO ❌ → ✅

```kotlin
// ERRADO (tem erro):
items(statusses) { status ->  // typo

// CORRETO:
items(statuses) { status ->   // apenas fixou o typo, nada mais
```

## EXEMPLO ERRADO ❌

```kotlin
// NÃO FAÇA ISTO:
fun EmptyScreen() {           // ← ADICIONADO (PROIBIDO!)
    Box { Text("") }
}

// NÃO FAÇA ISTO:
fun HttpCatItem(status) {     // ← REFATORADO (PROIBIDO!)
    val newVar = status       // ← ADICIONADO (PROIBIDO!)
    return newVar.display()
}
```

---

**RESUMO**: Se o commit não é APENAS "fix: minimal correction of [exact error]", algo deu errado.
