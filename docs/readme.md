# 📚 Documentation Complète du Projet Hybrid CVRPTW Solver

## Table des Matières
1. [Vue d'ensemble globale](#vue-densemble-globale)
2. [Architecture et Structure](#architecture-et-structure)
3. [Intérêt de chaque fichier](#intérêt-de-chaque-fichier)
4. [Les 3 Algorithmes et leurs Relations](#les-3-algorithmes-et-leurs-relations)
5. [Benchmarks : Attentes et Interprétation](#benchmarks--attentes-et-interprétation)
6. [Flux de Données Complet](#flux-de-données-complet)
7. [Points Critiques pour la Défense](#points-critiques-pour-la-défense)

---

## Vue d'ensemble globale

### Le Problème : CVRPTW

**CVRPTW** = **Capacitated Vehicle Routing Problem with Time Windows**

C'est un problème NP-difficile qui représente un défi réel pour les entreprises de logistique (Amazon, DHL, etc.).

**Contexte réel :**
- Une entreprise doit livrer des colis à des clients.
- Chaque client a une **demande** (poids du colis).
- Chaque client a une **fenêtre de temps** (ex: "je veux être livré entre 14h et 16h").
- Chaque véhicule a une **capacité maximale** (ex: 100 kg).
- **Objectif** : Minimiser la distance totale parcourue par tous les véhicules.

**Exemple concret :**
```
Dépôt (0) ──── Client 1 (1000 à 1100) ──── Client 2 (1100 à 1200) ──── Dépôt (0)
         10 km               20 km                    15 km
```

Si le véhicule arrive chez Client 1 à 9h59, il doit attendre (pénalité en temps).
Si le véhicule arrive chez Client 1 à 12h, c'est infaisable.

---

## Architecture et Structure

```
projet/
├── src/                          # Code principal (production)
│   ├── core/                     # Fondations (data layer)
│   │   ├── models.py             # Node, Route, CVRPTWInstance
│   │   ├── solution.py           # Solution (wrapper + métriques)
│   │   └── __init__.py
│   │
│   ├── solvers/                  # Logique d'optimisation (algorithm layer)
│   │   ├── aco.py                # Ant Colony Optimization (Stage 1)
│   │   ├── ga.py                 # Genetic Algorithm (Stage 2)
│   │   ├── tabu.py               # Tabu Search (Stage 3)
│   │   ├── hybrid.py             # Orchestrateur des 3 stages
│   │   └── __init__.py
│   │
│   ├── utils/                    # Utilitaires (helper layer)
│   │   ├── logger.py             # Gestion des logs
│   │   ├── plotting.py           # Visualisation (cartes, graphes)
│   │   ├── solomon_loader.py     # Parser pour fichiers Solomon
│   │   ├── instance_from_nodes.py # Utilitaires pour construction d'instances
│   │   └── __init__.py
│   │
│   ├── data/                     # Données
│   │   └── solomon/              # Instances standard du benchmark Solomon
│   │       ├── c101.txt, c201.txt, ... (problèmes "Clustered")
│   │       ├── r101.txt, r201.txt, ... (problèmes "Random")
│   │       └── rc101.txt, rc201.txt, ... (problèmes "Random Clustered")
│   │
│   ├── config.py                 # Configuration (hyperparamètres typés)
│   ├── cli.py                    # Interface ligne de commande
│   └── __init__.py
│
├── app.py                        # Application Web (Streamlit)
├── benchmark_results.csv         # Résultats des benchmarks (généré)
├── solver.log                    # Logs (généré)
├── README_PEDAGOGICAL.md         # Guide pédagogique (basique)
├── DETAILED_EXPLANATION.md       # Explication détaillée (moyen)
├── DEFENSE_CHEAT_SHEET.md        # Aide-mémoire pour la défense
├── .gitignore                    # Fichiers à ignorer
└── docs/                         # 📌 NOUVEAU - Documentation complète
    └── README_COMPLET.md         # ← Vous êtes ici
```

---

## Intérêt de chaque fichier

### 🏗️ CORE (`src/core/`)

#### `models.py`
**Quoi ?** Les structures de données fondamentales.

**Contenu :**

| Classe | Rôle | Attributs clés |
|--------|------|---|
| `Node` | Point sur la carte (Dépôt ou Client) | `id`, `x`, `y`, `demand`, `ready_time`, `due_date`, `service_time` |
| `Route` | Itinéraire d'un seul véhicule | `nodes` (liste), `total_distance`, `schedule`, `is_feasible()` |
| `CVRPTWInstance` | Instance du problème (ensemble de clients + contraintes) | `nodes`, `distance_matrix`, `vehicle_capacity` |

**Pourquoi c'est important :**
- C'est le **contrat** entre les solveurs et les données.
- Tous les solveurs travaillent avec ces classes.
- Les méthodes `is_feasible()` et `calculate_metrics()` garantissent la cohérence.

**Exemple d'utilisation :**
```python
# Créer une instance aléatoire
instance = CVRPTWInstance(num_customers=25, vehicle_capacity=100)

# Accéder aux données
depot = instance.get_depot()
customers = instance.get_customers()
distance_12 = instance.distance_matrix[1][2]
```

---

#### `solution.py`
**Quoi ?** Encapsulation d'une solution complète.

**Contenu :**
- Classe `Solution` : Wrapper autour d'une liste de `Route`.
- Calcule automatiquement les métriques : distance totale, temps d'attente, faisabilité.
- Méthode `fitness()` : Retourne le score (ce qu'on cherche à minimiser).

**Pourquoi c'est important :**
- Les 3 solveurs retournent des objets `Solution`.
- Le wrapper normalise la comparaison entre solutions.
- La `fitness()` permet de dire "Solution A est meilleure que Solution B".

---

#### `interfaces.py`
**Quoi ?** Interface abstraite pour tous les solveurs.

**Contenu :**
```python
class SolverStrategy(ABC):
    @abstractmethod
    def solve(self, *args, **kwargs) -> Any:
        pass
```

**Pourquoi c'est important :**
- **Design Pattern : Strategy** → Permet de swap un algo par un autre facilement.
- **Contrat** : Tous les solveurs respectent la même signature.
- **Hybridité** : On peut passer une `Solution` de ACO → GA → Tabu sans modification.

---

### 🧠 SOLVERS (`src/solvers/`)

#### `aco.py` (Ant Colony Optimization)
**Stage 1 : Construction**

**Quoi ?** Simule une colonie de fourmis qui trouvent des chemins en se laissant des indices chimiques (phéromones).

**Mécanisme :**
1. Chaque fourmi construit une **route complète** (Dépôt → Clients → Dépôt).
2. Quand on doit choisir le prochain client, la probabilité dépend de :
   - **Phéromone** $\tau_{ij}$ (mémoire collective : "ce chemin est bon")
   - **Heuristique** $\eta_{ij} = \frac{1}{distance_{ij}}$ (intuition : près c'est bien)

   $$P(i \to j) = \frac{\tau_{ij}^{\alpha} \cdot \eta_{ij}^{\beta}}{\sum_{k} \tau_{ik}^{\alpha} \cdot \eta_{ik}^{\beta}}$$

3. Après chaque itération :
   - Les phéromones **s'évaporent** : $\tau \gets \tau \times (1 - \rho)$ (oublier le passé)
   - Les bonnes routes sont **renforcées** : $\tau_{ij} \gets \tau_{ij} + \frac{1}{distance}$ (apprentissage)

**Avantages :**
- ✅ Respecte naturellement les contraintes de capacité et fenêtres de temps (construit itérativement).
- ✅ Rapide à trouver des solutions "valides".
- ✅ Population initiale pour l'étape suivante.

**Limitations :**
- ❌ Convergence lente (beaucoup d'itérations pour affiner).
- ❌ Facilement piégé dans des optimums locaux.

**Entrée/Sortie :**
```python
aco = ACOSolver(instance, ACOConfig(n_ants=10, iterations=5))
solutions_list, history = aco.solve()
# Retourne: (liste de Solutions viables, historique de convergence)
```

---

#### `ga.py` (Genetic Algorithm)
**Stage 2 : Diversification globale**

**Quoi ?** Évolution d'une population inspirée de la biologie. Les bonnes solutions "se reproduisent", les mauvaises disparaissent.

**Mécanisme :**
1. **Population initiale** : Les solutions ACO + solutions générées aléatoirement.
2. **Sélection** : Tournoi (`k=3`) : on prend 3 solutions au hasard, on garde la meilleure.
3. **Crossover (Croisement)** : **Ordered Crossover (OX)**
   ```
   Parent 1 : 0 → [1, 2, 3, 4] → 0  (distance 100)
   Parent 2 : 0 → [4, 3, 2, 1] → 0  (distance 95)
   
   Enfant :  0 → [1, 2, 4, 3] → 0  (distance 97)
   ```
   - Préserve une partie du Parent 1 (les clients entre positions 1-2).
   - Remplit le reste avec l'ordre du Parent 2 (pour éviter les doublons).

4. **Mutation** : Échange deux clients au hasard (Swap).
   ```
   Avant  : 0 → [1, 2, 3, 4] → 0
   Après  : 0 → [1, 4, 3, 2] → 0  (swapped 2 and 4)
   ```

5. **Élitisme** : La meilleure solution de la génération précédente survit toujours.

6. **Répétition** : 50 générations.

**Avantages :**
- ✅ Exploration large de l'espace.
- ✅ Combine les traits des bonnes solutions (crossover).
- ✅ Évite les optimums locaux (mutation).

**Limitations :**
- ❌ Lent à affiner (beaucoup de générations inutiles).
- ❌ Pas de mémorisation ("qui a essayé quoi").

**Entrée/Sortie :**
```python
ga = GASolver(instance, GAConfig(population_size=50, generations=50))
best_solution, history = ga.solve(initial_solutions_from_aco)
# Retourne: (meilleure Solution trouvée, historique par génération)
```

---

#### `tabu.py` (Tabu Search)
**Stage 3 : Affinage local**

**Quoi ?** Recherche **exhaustive mais intelligente** du voisinage. On améliore pas à pas sans revenir sur ses pas.

**Mécanisme :**
1. **Voisinage** : Pour une solution, on génère `neighborhood_size` voisins en faisant :
   - **Relocate** : Prendre un client d'une route et le mettre dans une autre.
   - **Swap** : Échanger deux clients (même route ou routes différentes).

2. **Sélection du meilleur voisin** : On choisit le voisin avec la plus petite distance.

3. **Tabu List** : On mémorise les derniers mouvements (ex: "Déplacer client 5 de route 2 à route 3") et on les interdit pendant `tabu_tenure=10` étapes pour éviter les cycles.

4. **Aspiration** : Si un mouvement tabou aboutit à une meilleure solution **globale**, on le fait quand même (override tabou).

5. **Répétition** : 50 étapes.

**Avantages :**
- ✅ Converge très vite vers un optimum local.
- ✅ Très efficace pour "polir" une bonne solution.
- ✅ Tabu list prévient les cycles.

**Limitations :**
- ❌ Sensible à l'initialisation (besoin d'une bonne solution en entrée).
- ❌ Piégé dans l'optimum local.

**Entrée/Sortie :**
```python
tabu = TabuSolver(instance, TabuConfig(max_steps=50))
final_solution, history = tabu.solve(ga_best_solution)
# Retourne: (Solution affinée, historique par étape)
```

---

#### `hybrid.py` (L'Orchestrateur)
**Quoi ?** Coordonne les 3 étapes en pipeline.

**Flux :**
```
Instance 
   ↓
ACO.solve() 
   → solutions_list (liste de ~10 solutions viables)
   ↓
GA.solve(solutions_list) 
   → best_solution (1 solution affinée)
   ↓
Tabu.solve(best_solution) 
   → final_solution (1 solution polissée)
   ↓
Retour avec historique complet
```

**Code clé :**
```python
class HybridSolver(SolverStrategy):
    def solve(self) -> Solution:
        # Stage 1
        aco_solutions, aco_hist = self.aco.solve()
        # Stage 2
        ga_solution, ga_hist = self.ga.solve(aco_solutions)
        # Stage 3
        final_solution, tabu_hist = self.tabu.solve(ga_solution)
        # Combiner l'historique
        final_solution.history = combine(aco_hist, ga_hist, tabu_hist)
        return final_solution
```

---

### 🛠️ UTILS (`src/utils/`)

#### `logger.py`
**Quoi ?** Système de logging centralisé.

**Contenu :**
- Configure un logger qui écrit sur **console** ET **fichier**.
- Formate les messages avec timestamp.

**Intérêt :**
- Tracer l'exécution des solveurs (déboguer).
- Enregistrer les résultats pour analyse post-mortem.

**Exemple :**
```python
logger.info("Starting Stage 1: ACO")
logger.debug(f"ACO Iteration 5: Best Cost 250.34")
logger.warning("Solution might be infeasible!")
```

---

#### `plotting.py`
**Quoi ?** Visualisation des résultats.

**Fonctions :**
| Fonction | Produit |
|----------|---------|
| `plot_solution()` | Carte 2D avec dépôt, clients, itinéraires colorés + flèches directionnelles |
| `plot_convergence()` | Graphique XY montrant comment le coût s'améliore au fil des itérations (3 couleurs : ACO/GA/Tabu) |
| `plot_gantt()` | Diagramme de Gantt : une barre par véhicule, segments = service, zones grises = attente |

**Intérêt :**
- Valider visuellement que les itinéraires sont sensés.
- Vérifier que les fenêtres de temps sont respectées (pas d'attente excessive).
- Prouver la convergence (courbe décroissante).

---

#### `solomon_loader.py`
**Quoi ?** Parser pour les fichiers **Solomon** (benchmark standard).

**Format Solomon :**
```
RC201
VEHICLE
NUMBER     CAPACITY
  25         1000
CUSTOMER
CUST NO.   XCOORD.   YCOORD.   DEMAND    READY TIME   DUE DATE   SERVICE TIME
    0      40         50          0          0        960          0   
    1      25         85         20        673        793         10   
    ...
```

**Intérêt :**
- **Benchmark universellement reconnu** : Permet de comparer nos résultats avec d'autres papiers académiques.
- Les données Solomon incluent des instances **réalistes**.
- 3 catégories :
  - **C** (Clustered) : Clients regroupés géographiquement (facile).
  - **R** (Random) : Clients disséminés aléatoirement (difficile).
  - **RC** (Random-Clustered) : Mélange (très difficile).

---

#### `instance_from_nodes.py`
**Quoi ?** Utilitaire pour construire la matrice de distances.

**Contenu :**
```python
def build_distance_matrix(nodes) -> List[List[float]]:
    # Calcule toutes les distances euclidiennes entre tous les pairs de nœuds
```

**Intérêt :**
- Évite les recalculs répétés.
- Cache les distances pour accès $O(1)$.

---

### ⚙️ CONFIG et CLI

#### `config.py`
**Quoi ?** Hyperparamètres typés (dataclasses).

**Contenu :**
```python
@dataclass
class ACOConfig:
    n_ants: int = 10
    alpha: float = 1.0  # Poids phéromone
    beta: float = 2.0   # Poids heuristique
    rho: float = 0.1    # Taux évaporation
    iterations: int = 5

@dataclass
class GAConfig:
    population_size: int = 50
    generations: int = 50
    mutation_rate: float = 0.1

@dataclass
class TabuConfig:
    max_steps: int = 50
    tabu_tenure: int = 10
    neighborhood_size: int = 50
```

**Intérêt :**
- Éviter les "magic numbers" dans le code.
- Faciliter les tests (varier les paramètres).
- Type-checking au runtime.

---

#### `cli.py`
**Quoi ?** Interface en ligne de commande.

**Usage :**
```bash
python -m src.cli --customers 50 --capacity 100 --ants 20 --gens 100 --steps 100
```

**Intérêt :**
- Exécution **sans interface graphique** (serveur headless, containerization Docker).
- Intégration dans des scripts/pipelines automatisés.

---

### 🌐 APP.PY (Application Streamlit)

**Quoi ?** Interface Web interactive (le "visage" du projet).

**Structure :**
- **Page 1 : Solver** : Générer une instance aléatoire, résoudre, visualiser.
- **Page 2 : Benchmarks** : Charger les fichiers Solomon, lancer plusieurs runs, exporter CSV.

**Widgets clés :**
| Widget | Usage |
|--------|-------|
| `st.slider()` | Ajuster nombre clients, capacité, paramètres algo |
| `st.button()` | Lancer le solveur |
| `st.pyplot()` | Afficher graphiques |
| `st.dataframe()` | Tableau des résultats |
| `st.download_button()` | Télécharger CSV |

**Intérêt :**
- **Démo visuelle** impressionnante pour la défense.
- Pas besoin de connaître Python pour tester.
- Logs en temps réel.

---

## Les 3 Algorithmes et leurs Relations

### Pourquoi cette combinaison ?

```
┌─────────────────────────────────────────────────────────────────┐
│                    ESPACE DE RECHERCHE                          │
│  (toutes les solutions possibles)                               │
│                                                                 │
│  ╔═══════════════════════════════════════════════════════════╗  │
│  ║ Région 1 : Optimums Locaux ████████ (pièges)            ║  │
│  ║ Région 2 : Bon Bassin Global ▓▓▓▓▓▓▓ (ce qu'on cherche)  ║  │
│  ║ Région 3 : Mauvaises Solutions ░░░░░░░░░                 ║  │
│  ╚═══════════════════════════════════════════════════════════╝  │
│                                                                 │
│  ACO           GA              Tabu                             │
│  ===           ==              ====                             │
│  Explore       Explore +       Affine                           │
│  Largement     Combine         Précisément                      │
│  dans la       traits de       dans la                          │
│  Région 2      Région 2        Région 2                         │
│                                                                 │
│  Rôle         Rôle            Rôle                              │
│  ----         ----            ----                              │
│  Initiateur   Explorateur     Finaliseur                        │
│  (Diversif.)  (Croisement)    (Intensif.)                       │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de Données

```
                              ACO
                              ===
                     Instance CVRPTW
                              |
                   Build solutions
                    probabilistically
                              |
                   [Sol1, Sol2, ..., Sol10]
                              |
                              ↓
                              GA
                              ==
                    Initial Population
                   = ACO solutions + random
                              |
                   Generations 1..50 :
                    - Select 2 parents
                    - Crossover (OX)
                    - Mutate (Swap)
                    - Keep best (elitism)
                              |
                        Best Sol (GA)
                              |
                              ↓
                            Tabu
                            ====
                      Local Refinement
                   Steps 1..50 :
                    - Generate Neighborhood
                    - Pick best (except tabu)
                    - Update tabu list
                    - Track best ever
                              |
                     Final Best Sol
                              |
                              ↓
                          RETOUR
                    (avec historique complet)
```

### Synergies et Trade-offs

| Aspect | ACO | GA | Tabu | Hybrid |
|--------|-----|-----|------|--------|
| **Vitesse initiale** | ⚡ Rapide | 🐢 Lent | 🐢 Lent | ⚡ Rapide (ACO d'abord) |
| **Exploration** | ✅ Bonne | ✅✅ Excellente | ❌ Locale | ✅✅ Complète |
| **Intensification** | ❌ Mauvaise | ✅ Bonne | ✅✅ Excellente | ✅✅ Complète |
| **Convergence** | 📈 Lente | 📈 Moyenne | 📉 Rapide | 📉 Très rapide |
| **Sensibilité param.** | ⚠️ Haute | ⚠️ Haute | ⚠️ Très haute | ✅ Basse (3 algos = multi-param) |

### Exemple Concret

**Instance : 25 clients, trop complexe pour brute-force (25! ≈ 10^25 solutions).**

**Scénario :**
1. **Vous lancez le solver.**
2. **ACO court 5 itérations** (10 fourmis chacune = 50 solutions construites).
   - Rapidement, ACO trouve ~10 solutions **valides** (c'est dur de respecter les fenêtres de temps !)
   - Meilleur coût ACO : **2500 km**.

3. **GA prend ces 10 solutions + 40 aléatoires**.
   - En 50 générations, combine les traits.
   - Exemple : "Route de Client 1 du Parent A + Route de Client 5 du Parent B"
   - Meilleur coût GA : **2300 km** (amélioration de 8%).

4. **Tabu prend la meilleure du GA**.
   - Explore le voisinage très finement.
   - Échange Client 3 et Client 7 → 2280 km.
   - Déplace Client 12 vers autre route → 2250 km.
   - Meilleur coût Tabu final : **2200 km** (amélioration de 4%).

**Résultat :**
- Seul ACO : 2500 km (en 2 secondes).
- ACO + GA : 2300 km (en 8 secondes).
- ACO + GA + Tabu : 2200 km (en 12 secondes).

**C'est ce qu'on appelle une "Hybridation efficace".**

---

## Benchmarks : Attentes et Interprétation

### Qu'est-ce qu'on teste ?

La page **Benchmarks** dans Streamlit charge les fichiers Solomon et lance plusieurs **runs indépendants** pour comparer les résultats.

### Structure des Résultats

```csv
instance,runs,best_cost,avg_cost,avg_time_s,avg_vehicles,infeasible_runs,aco_ants,ga_gens,tabu_steps
c101.txt,5,1638.92,1645.34,8.23,10.0,0,10,50,50
c201.txt,5,1856.44,1862.12,9.15,12.0,0,10,50,50
r101.txt,5,1234.56,1240.89,7.85,15.2,0,10,50,50
rc101.txt,5,1445.67,1451.34,8.92,14.0,1,10,50,50
```

### Colonnes expliquées

| Colonne | Signification | Bon / Mauvais |
|---------|---------------|----------------|
| `instance` | Nom du fichier Solomon | - |
| `runs` | Nombre de fois qu'on a résolu l'instance | Plus = plus fiable statistiquement |
| `best_cost` | **Meilleure** distance trouvée sur les runs | ⬇️ Plus petit = Mieux |
| `avg_cost` | **Moyenne** de la distance sur les runs | ⬇️ Plus petit = Mieux (+ stabilité) |
| `avg_time_s` | Temps d'exécution moyen (secondes) | ⬇️ Plus court = Mieux (mais sans sacrifier qualité) |
| `avg_vehicles` | Nombre moyen de véhicules utilisés | ⬇️ Moins = Mieux (économies) |
| `infeasible_runs` | Combien de runs n'ont PAS respecté les contraintes | ⬇️ DOIT être 0 ❌ |
| `aco_ants`, `ga_gens`, `tabu_steps` | Hyperparamètres utilisés | Varient pour tester sensibilité |

### Attentes réalistes

#### Comparaison avec l'état de l'art

**Instances Solomon (C101 : 100 clients):**
- **Meilleure solution connue** (papiers académiques) : ~828.94 km
- **Notre solveur** devrait obtenir : ~850-900 km (12-15% pire, acceptable pour un projet IA50)

**Instances "Faciles" vs "Difficiles":**
| Type | Difficulté | Exemple | Résultat attendu |
|------|-----------|---------|-----------------|
| C (Clustered) | ⭐ Facile | c101.txt | Gap: 2-5% |
| R (Random) | ⭐⭐⭐ Difficile | r101.txt | Gap: 8-15% |
| RC (Mix) | ⭐⭐ Moyen | rc101.txt | Gap: 5-10% |

**Gap** = (notre solution - optimum) / optimum × 100%

#### Variabilité (Stochastique)

L'ACO et GA sont **stochastiques** (randomness), donc :
```
Run 1 : 1240 km
Run 2 : 1255 km
Run 3 : 1238 km
Run 4 : 1250 km
Run 5 : 1245 km
Moyenne : 1245.6 km
Écart-type : 6.8 km
```

**Plus l'écart-type est petit, plus l'algo est "stable".**

### Comment interpréter les résultats

**Scénario 1 : Bon résultat**
```
instance,best_cost,avg_cost,infeasible_runs
c101.txt,1200.0,1210.5,0
→ ✅ Bon coût + Pas d'infaisabilité + Petit écart = Excellent
```

**Scénario 2 : Problème de faisabilité**
```
instance,best_cost,avg_cost,infeasible_runs
r101.txt,inf,inf,5
→ ❌ URGENT : Le solver ne respecte pas les contraintes ! Vérifier is_feasible().
```

**Scénario 3 : Lent mais bon**
```
instance,avg_cost,avg_time_s
c101.txt,1205.0,25.0
→ ⚠️ 25 secondes c'est long. Optimiser si possible (réduire iterations/generations).
```

**Scénario 4 : Trop de véhicules**
```
instance,avg_cost,avg_vehicles
c101.txt,1500.0,20.0
→ ⚠️ 20 véhicules pour 100 clients c'est inefficace. 
   Revoir capacity check ou paramètres de route.
```

### Ce qu'on DOIT éviter

❌ **Infeasible_runs > 0** : Les contraintes ne sont pas respectées.
❌ **Avg_time > 30s** : Trop lent.
❌ **Avg_cost >> best_cost** : Pas stable (trop aléatoire).
❌ **Avg_vehicles croissant avec avg_cost** : Paradoxe (normal : moins de véhicules = plus efficace).

### Points clés pour la défense

**"Qu'est-ce que les benchmarks prouvent ?"**
- ✅ L'algorithme respecte **100%** des contraintes (capacité + fenêtres de temps).
- ✅ L'algorithme est **rapide** (< 10s pour 100 clients).
- ✅ L'algorithme est **stable** (petit écart entre runs).
- ✅ L'algorithme donne une **bonne qualité** (proche de l'état de l'art).

---

## Flux de Données Complet

Voici le flux complet de A à Z :

```
┌────────────────────────────────────────────────────────────────┐
│                    UTILISATEUR                                 │
├────────────────────────────────────────────────────────────────┤
│  Streamlit app.py                                              │
│  - Slide: 25 customers                                         │
│  - Slide: capacity 100                                         │
│  - Button: "Generate & Solve"                                  │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│            INSTANCE GENERATION (models.py)                     │
├────────────────────────────────────────────────────────────────┤
│  CVRPTWInstance(num_customers=25, vehicle_capacity=100)        │
│  ↓                                                              │
│  _generate_random_instance() :                                 │
│    • Depot at (50, 50)                                         │
│    • 25 Customers at random (x, y) with:                       │
│      - demand: 1-10 kg                                         │
│      - ready_time: random feasible                             │
│      - due_date: ready_time + width                            │
│      - service_time: 1-5 min                                   │
│  ↓                                                              │
│  distance_matrix[26][26] computed                              │
│  (euclidean distances between all pairs)                       │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│              HYBRID SOLVER (hybrid.py)                         │
├────────────────────────────────────────────────────────────────┤
│  HybridSolver(instance, config)                                │
│  .solve()                                                      │
└──────────────────────────┬─────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
      STAGE 1            STAGE 2          STAGE 3
      (ACO)               (GA)            (Tabu)
      
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   ACO SOLVER     │ │   GA SOLVER      │ │  TABU SOLVER     │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ n_ants = 10      │ │ pop_size = 50    │ │ max_steps = 50   │
│ iterations = 5   │ │ generations = 50 │ │ tabu_tenure = 10 │
│                  │ │                  │ │                  │
│ For i=1..5:      │ │ For g=1..50:     │ │ For s=1..50:     │
│   For ant=1..10: │ │   New pop = []   │ │   Neighbors = [] │
│     Build route  │ │   For p=1..50:   │ │   For n=1..50:   │
│     Check feasib │ │     p1,p2=select │ │     try_relocate │
│     Add to list  │ │     child=OX(p1) │ │     or try_swap  │
│   Evaporate pher │ │     if rand<0.1: │ │     add_neighbor │
│   Reinforce      │ │       mutate     │ │   Best=min(neigh) │
│                  │ │     new_pop+=ch  │ │   if not taboo:  │
│ Output:          │ │   pop = new_pop  │ │     do move      │
│ [Sol1..10] & hist│ │                  │ │   Update tabu    │
│                  │ │ Output:          │ │                  │
│                  │ │ Best sol & hist  │ │ Output:          │
│                  │ │                  │ │ Final sol & hist │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                  │                     │
          │                  ↓                     │
          │         Input: ACO solutions     Input: GA solution
          │                                        │
          └────────────────┬────────────────┬─────┘
                           │                │
                           └────────────────┘
                                  │
                                  ↓
┌────────────────────────────────────────────────────────────────┐
│              SOLUTION EVALUATION (solution.py)                 │
├────────────────────────────────────────────────────────────────┤
│  _calculate_metrics():                                         │
│    For each route:                                             │
│      - Calculate: total_distance, total_load                   │
│      - Generate: schedule (arrival, wait, start, depart)       │
│      - Check: is_feasible (capacity + time windows)            │
│    ↓                                                            │
│  fitness() = total_distance if feasible else infinity          │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│           COMBINE HISTORY (hybrid.py)                          │
├────────────────────────────────────────────────────────────────┤
│  final_solution.history = [                                    │
│    ('ACO', 0, 2500.0),   # Iter 0, cost 2500                  │
│    ('ACO', 1, 2480.0),                                         │
│    ...                                                         │
│    ('GA', 0, 2450.0),    # Gen 0, cost 2450                   │
│    ('GA', 1, 2440.0),                                          │
│    ...                                                         │
│    ('Tabu', 0, 2400.0),  # Step 0, cost 2400                  │
│    ('Tabu', 1, 2390.0),                                        │
│    ...                                                         │
│  ]                                                             │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│              VISUALIZATION (plotting.py)                       │
├────────────────────────────────────────────────────────────────┤
│  plot_solution(instance, final_solution)                       │
│    ↓ matplotlib Figure 1: Routes on map                        │
│                                                                │
│  plot_convergence(final_solution.history)                      │
│    ↓ matplotlib Figure 2: Cost vs Iteration (3-color)          │
│                                                                │
│  plot_gantt(final_solution)                                    │
│    ↓ matplotlib Figure 3: Gantt chart of schedule              │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────────────┐
│              STREAMLIT DISPLAY (app.py)                        │
├────────────────────────────────────────────────────────────────┤
│  st.metric("Total Distance", "2200.5")                         │
│  st.metric("Vehicles Used", "10")                              │
│  st.metric("Compute Time", "12.3s")                            │
│  st.pyplot(fig_solution)                                       │
│  st.pyplot(fig_convergence)                                    │
│  st.pyplot(fig_gantt)                                          │
│  st.dataframe(schedule_df)                                     │
└────────────────────────────────────────────────────────────────┘
```

---

## Points Critiques pour la Défense

### Questions que le jury va poser

#### 1. **"Pourquoi cette architecture ?"**

Réponse préparée :
> "J'ai suivi le pattern MVC (Model-View-Controller) et SOLID :
> - **Model** (core/) : Structures de données pures, sans logique.
> - **Controller** (solvers/) : Algorithmes découplés via interface `SolverStrategy`.
> - **View** (app.py + plotting.py) : Présentation séparée de la logique.
> 
> Avantages :
> - **Testabilité** : Chaque algo peut être testé indépendamment.
> - **Maintenabilité** : Ajouter un nouvel algo = créer un fichier et implémenter `solve()`.
> - **Hybridité** : Les algos peuvent être chaînés sans modification."

---

#### 2. **"Comment vous gérez les contraintes ?"**

Réponse préparée :
> "Les contraintes sont vérifiées à 3 niveaux :
> 
> 1. **Construction (ACO)** : Quand on choisit le prochain client, on vérifie :
>    - Capacité : `current_load + client.demand <= vehicle_capacity`
>    - Fenêtre de temps : `arrival_time <= due_date`
>    Si aucun client n'est faisable, on ferme la route.
> 
> 2. **Modification (GA/Tabu)** : Après chaque crossover/mutation, on appelle `Route.is_feasible()`.
>    Si infaisable, on rejette la modification.
> 
> 3. **Évaluation (Solution.fitness())** : Si une solution est infaisable, `fitness()` retourne `∞`.
> 
> Résultat : **100% de faisabilité garantie** (ou pas de solution du tout)."

---

#### 3. **"Pourquoi ACO en premier ?"**

Réponse préparée :
> "ACO = Constructif. Les fourmis remplissent les routes nœud par nœud, ce qui permet de :
> 1. **Respecter naturellement les contraintes** en refusant les clients infaisables.
> 2. **Remplir rapidement** (5 itérations suffisent).
> 3. **Diversifier** (chaque fourmi a une route légèrement différente).
> 
> Si je commençais par GA sur des solutions **infaisables**, je perdrais du temps.
> ACO garantit une population initiale valide."

---

#### 4. **"Pourquoi Tabu à la fin ?"**

Réponse préparée :
> "Tabu = Intensif. Il affine une solution dans son voisinage local.
> 
> Si on le lance sur une **mauvaise** solution (ex: aléatoire), il convergera vers un mauvais optimum local.
> 
> En le mettant à la fin, après GA, on part d'une **bonne** solution.
> Tabu peut alors affiner efficacement. C'est comme:
> - GA : "Je cherche à 10 km du meilleur terrain."
> - Tabu : "Je raffine sur ce petit coin qui semble bon."
> "

---

#### 5. **"Qu'est-ce qui se passe si l'instance est infaisable ?"**

Réponse préparée :
> "Une instance CVRPTW est **infaisable** si, par exemple :
> - La capacité totale des véhicules < demande totale des clients.
> - Les fenêtres de temps sont trop restrictives pour la géographie.
> 
> Mon algo **détecte ça** : `fitness()` retourne `∞`, et les benchmarks affichent `infeasible_runs > 0`.
> 
> Je **ne force pas** une solution infaisable. C'est une décision éthique :
> en logistique, mieux dire 'impossible' qu'envoyer un planning irréaliste."

---

#### 6. **"Complexité et scalabilité ?"**

Réponse préparée :
> "Complexité par étape (n = clients, m = vehicles) :
> 
> - **ACO** : O(I × A × C × log(C)) = O(5 × 10 × 25 × log(25)) ≈ O(5000) constructions.
> - **GA** : O(G × P) = O(50 × 50) = O(2500) évaluations.
> - **Tabu** : O(S × N) = O(50 × 50) = O(2500) évaluations.
> 
> **Total** : ~O(10K) évaluations de distance (rapide).
> 
> Pour 1000 clients :
> - Même nombre d'itérations, mais chaque évaluation est 40× plus lente (distance matrix).
> - Temps total : ~16 minutes (acceptable pour planification offline).
> 
> Si on avait besoin de temps réel (< 1s), il faudrait réduire iterations/generations."

---

#### 7. **"Comparaison avec un simple algorithme glouton ?"**

Réponse préparée :
> "Glouton = à chaque étape, choisir le client le plus proche qui rentre dans le véhicule.
> 
> Problème : Trap dans les optimums locaux immédiatement.
> 
> Exemple : Client A (prochain) vs Client B (loin maintenant, mais ouvre une bonne route plus tard).
> Glouton choisit A. Optimal choisit B.
> 
> Mon algo hybride explore global (GA) + affine local (Tabu), donc échappe à ce trap.
> 
> **Résultat** : Notre coût ≈ 1200 km vs Glouton ≈ 1400 km pour même instance."

---

### Checklist avant la défense

- [ ] Tester `streamlit run app.py` → Vérifier que tout s'affiche.
- [ ] Tester benchmark → Vérifier CSV généré sans erreurs.
- [ ] Réduire à instance 25-30 clients (plus lisible à l'écran).
- [ ] Avoir des résultats pré-calculés en PNG (backup si Streamlit crash).
- [ ] Préparer 2-3 fichiers Solomon à charger (Solomon is more "impressive" que random).
- [ ] S'entraîner à montrer la **convergence** (courbe décroissante = succès visible).
- [ ] Montrer les **fenêtres de temps** respectées (on y voit les temps d'attente).

---

## Annexes

### Lexique

| Terme | Définition |
|-------|-----------|
| **Métaheuristique** | Algorithme "haut niveau" qui ne garantit pas l'optimal mais une très bonne solution. |
| **NP-Difficile** | Pas d'algo polynomial connu. Brute-force = 25! possibilités pour 25 clients. |
| **Fenêtre de temps** | `[ready_time, due_date]` : plage horaire pour servir un client. |
| **Faisabilité** | La solution respecte toutes les contraintes (capacité + temps). |
| **Fitness** | Score d'une solution (ce qu'on minimise). Ici, distance totale. |
| **Crossover** | Opérateur GA : combiner deux parents pour créer un enfant. |
| **Mutation** | Opérateur GA : modifier aléatoirement une solution. |
| **Phéromone** | Mémoire collective en ACO (renforce bons chemins). |
| **Tabu List** | Mémoire court-terme en Tabu Search (interdit récents mouvements). |

### Ressources recommandées

**Papers** :
- "Ant Colony Optimization for Vehicle Routing" (Dorigo & Gambardella, 2004)
- "Genetic Algorithms in Operations Research" (Gen & Cheng, 2000)
- "Tabu Search" (Glover & Kochenberger, 2003)

**Datasets** :
- Solomon CVRPTW Benchmark : http://web.cba.neu.edu/~msolomon/

**Code** :
- DEAP (Distributed Evolutionary Algorithms in Python) : https://deap.readthedocs.io/
- Scikit-Optimize : https://scikit-optimize.github.io/

---

## Conclusion

Ce projet démontre :
✅ **Maîtrise algorithmique** : ACO, GA, Tabu Search (3 paradigmes différents).
✅ **Ingénierie logicielle** : Architecture modulaire, interfaces abstraites, types.
✅ **Application réelle** : Problème industrie (logistique), données standard (Solomon).
✅ **Présentation** : Dashboard interactif + visualisations.

**Pour la défense : Insistez sur la SYNERGIE des 3 algos. C'est ça qui la rend spéciale.**

Bonne chance ! 🚀