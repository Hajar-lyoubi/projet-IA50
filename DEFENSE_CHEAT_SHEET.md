# 🚀 Defense Day Cheat Sheet

Gardez ce fichier ouvert le jour J. Voici la procédure exacte pour une démo parfaite.

## 1. Préparation (5 min avant)
Ouvrez votre terminal et assurez-vous d'être dans le dossier du projet :
```bash
cd /chemin/vers/le/projet
```

## 2. La Démo Visuelle (L'effet "Wow")
C'est ce que vous montrez au jury en premier.
Lancez le dashboard :
```bash
streamlit run app.py
```
**Ce qu'il faut montrer :**
1.  **Sidebar** : Montrez que vous pouvez configurer le nombre de clients (mettez 25 pour que ça soit lisible).
2.  **Bouton** : Cliquez sur "Generate Instance & Solve".
3.  **Carte** : Montrez les routes colorées.
4.  **Graphe de Convergence** : Expliquez "Regardez comment l'algorithme s'améliore : ACO trouve une base, GA explore, et Tabu affine le résultat final."
5.  **Gantt Chart** : Montrez les barres grises. "Les barres grises représentent les temps d'attente. Mon algo respecte les fenêtres de temps."

## 3. La Démo Technique (L'effet "Expert")
Si le prof demande "Et si je veux lancer ça sur un serveur sans écran ?", lancez le CLI :
```bash
python3 -m src.cli --customers 50 --ants 20 --steps 100
```
Expliquez : "J'ai conçu une architecture modulaire qui permet d'exécuter le solveur en mode headless pour des calculs intensifs."

## 4. Inspection du Code (Si demandé)
Ouvrez `src/config.py` et `src/interfaces.py`.
Dites : "J'ai utilisé des **Dataclasses** pour la configuration et des **Interfaces Abstraites** pour assurer l'extensibilité du projet. C'est une architecture de niveau industriel."

---
**Bonne chance ! Vous avez un projet solide.** 🍀
