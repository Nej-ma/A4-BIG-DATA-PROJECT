# Instructions pour exporter le schéma en SVG

## Option 1 : Via mermaid.live (RECOMMANDÉ)

1. Ouvrir https://mermaid.live
2. Copier le contenu du fichier `SCHEMA_MERMAID_VISUEL.mmd`
3. Coller dans l'éditeur mermaid.live
4. Cliquer sur "Actions" → "Export SVG"
5. Sauvegarder sous le nom `diagramme_dimensions.svg`
6. Placer le fichier dans le dossier `projet/`

## Option 2 : Via le fichier HTML

1. Ouvrir `SCHEMA_MERMAID_VISUEL_HTML.html` dans votre navigateur
2. Faire clic droit sur le diagramme
3. "Inspecter l'élément"
4. Copier le code SVG généré
5. Sauvegarder dans un fichier `diagramme_dimensions.svg`

## Option 3 : Utiliser l'alternative PNG

Si SVG pose problème :
1. Sur mermaid.live, exporter en PNG haute résolution
2. Nommer le fichier `diagramme_dimensions.png`
3. Modifier la ligne dans le LaTeX : `\includegraphics[width=\textwidth]{diagramme_dimensions.png}`
