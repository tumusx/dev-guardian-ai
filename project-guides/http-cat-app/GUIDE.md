# HTTP Cat App - Guia de Estrutura

## ⚠️ INSTRUÇÕES CRÍTICAS PARA CORREÇÕES

### NÃO FAZER (nunca adicione isso):
- ❌ `defaultStatuses` - NÃO EXISTE
- ❌ `status.description` - Campo NÃO EXISTE  
- ❌ `status.getDisplayText()` - NÃO EXISTE
- ❌ Novos imports não mencionados
- ❌ Novos métodos ou classes
- ❌ Refatorar ou melhorar código
- ❌ Mudar lógica existente

### Classes Existentes

**HttpCatStatus**
```kotlin
data class HttpCatStatus(
    val code: Int,
    val imageUrl: String
)
```
Métodos: `getDisplayText()` para exibir o código

**HttpCatService**
```kotlin
interface HttpCatService {
    suspend fun fetchAllStatuses(): List<HttpCatStatus>
}
```

### Estrutura do App

```
MainActivity.kt
├── MainActivity (Activity)
├── HttpCatApp() - Composable
├── HttpCatContent() - Composable
├── HttpCatItem() - Composable
└── HttpCatStatus data class
```

### Imports Permitidos
```kotlin
import androidx.compose.material3.*
import androidx.compose.foundation.layout.*
import coil3.compose.AsyncImage
import io.ktor.client.*
import kotlinx.coroutines.*
```

### Exemplos de Correção CORRETA

**CORRETO: Adicionar parênteses faltando**
```kotlin
// Antes (ERRADO):
Column
    modifier = Modifier.padding(16.dp)

// Depois (CORRETO):
Column(
    modifier = Modifier.padding(16.dp)
) {
```

**CORRETO: Typo em nome**
```kotlin
// Antes (ERRADO):
items(HttpCatStatu) { status ->

// Depois (CORRETO):
items(statuses) { status ->
```

**ERRADO: Adicionar campos**
```kotlin
// NÃO FAÇA ISSO:
Text(
    text = status.description,  // ❌ Campo não existe!
    ...
)
```

## Regra de Ouro

**APENAS CORRIJA O ERRO DE SINTAXE/TIPO EXATO.**
Não adicione nada novo. Não mude lógica. Não refatore.
Se não sabe o que fazer, não mude nada que não cause o erro.
