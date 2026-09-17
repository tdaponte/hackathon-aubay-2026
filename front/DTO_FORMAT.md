# Format du DTO - Champs de formulaire

## Version 2 (Actuelle)

Le format du JSON envoyé par l'autre application a changé.

### Structure

```json
{
  "field": {
    "request": "string",      // La question à afficher
    "type": "string",         // Type de champ: "text", "checkbox", "dropdown"
    "values": ["string"],     // Valeurs possibles (pour dropdown)
    "example": "string",      // Exemple affiché sous la question
    "optional": boolean       // Si le champ est optionnel
  },
  "response_url": "string"    // URL où envoyer la réponse
}
```

### Exemple complet

```json
{
  "field": {
    "request": "Est-ce que tu peux te présenter ?",
    "type": "text",
    "values": [],
    "example": "Je m'appelle Nicolas Dupont, je suis né en 1983 à Montpellier et je suis inspecteur des impôts.",
    "optional": false
  },
  "response_url": "http://localhost:8502/mock_response"
}
```

### Champs

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `request` | string | ✅ | La question à afficher à l'utilisateur |
| `type` | string | ✅ | Type de champ: `text`, `checkbox`, `dropdown` |
| `values` | string[] | ❌ | Valeurs possibles (pour dropdown, vide pour text) |
| `example` | string | ❌ | Exemple pour guider l'utilisateur |
| `optional` | boolean | ❌ | Si le champ peut être sauté (défaut: false) |
| `response_url` | string | ✅ | URL où envoyer la réponse (POST) |

### Types de champs supportés

#### `text`
Champ texte simple.

```json
{
  "request": "Quel est votre nom ?",
  "type": "text",
  "example": "Jean Dupont"
}
```

#### `checkbox`
Case à cocher (implémenté, non visible dans l'UI actuelle).

```json
{
  "request": "Acceptez-vous les conditions ?",
  "type": "checkbox",
  "example": "Oui"
}
```

#### `dropdown`
Liste déroulante (à implémenter dans l'UI).

```json
{
  "request": "Choisissez votre région",
  "type": "dropdown",
  "values": ["Île-de-France", "Provence", "Bretagne"],
  "example": "Île-de-France"
}
```

### Réponse de l'utilisateur

Quand l'utilisateur valide, Streamlit envoie:

```json
{
  "response": "La réponse de l'utilisateur"
}
```

À l'URL fournie en `response_url`.

## Ancienne version (v1)

```json
{
  "type": "text",
  "text": "Quel est votre nom ?",
  "placeholder": "Entrez votre réponse"
}
```

Cette version n'est plus supportée.
