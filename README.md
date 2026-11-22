# abc-lettres

Application pour apprendre à écrire les lettres de l'alphabet, en français et en anglais, sur tablette.

- Menu avec 4 modules : majuscules A-Z, minuscules a-z (script, sur 4 lignes d'écriture), chiffres 0-10, jeux
- 4 étapes par lettre ou chiffre : regarder, suivre la route, ramasser les objets, écrire tout seul
- Jeux : bulles, images, grande lettre / petite lettre, compter
- Un personnage différent à chaque lettre, des étoiles par étape, des autocollants à collectionner
- Voix enregistrées : Siwis (Piper) en français, Heart (Kokoro) en anglais
- Fonctionne hors ligne une fois installée sur l'écran d'accueil
- Espace parent : appui long de 1,5 s sur ⚙️ (réglages, progression, sauvegarde)

## Fichiers

- `index.html` : l'application complète
- `audio/` : toutes les phrases enregistrées (un fichier mp3 et un index json par langue)
- `manifest.json`, `icons/` : installation sur l'écran d'accueil
- `sw.js` : mode hors ligne. Changer `VERSION` quand les fichiers audio ou les icônes changent.
