# abc-lettres

Application pour apprendre à écrire les lettres de l'alphabet, en français et en anglais, sur tablette.

- 26 majuscules, en 4 étapes par lettre : regarder, suivre la route, ramasser les objets, écrire tout seul
- Un personnage différent à chaque lettre, des étoiles par étape, des autocollants à collectionner
- Voix enregistrées : Siwis (Piper) en français, Heart (Kokoro) en anglais
- Fonctionne hors ligne une fois installée sur l'écran d'accueil
- Espace parent : appui long de 1,5 s sur ⚙️ (réglages, progression, sauvegarde)

## Fichiers

- `index.html` : l'application complète
- `audio/` : toutes les phrases enregistrées (un fichier mp3 et un index json par langue)
- `manifest.json`, `icons/` : installation sur l'écran d'accueil
- `sw.js` : mode hors ligne. Changer `VERSION` quand les fichiers audio ou les icônes changent.
