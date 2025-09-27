## Programming Steps

The first step is to retrieve the commits from the target repository `passerelle`.
To do this, you must first clone the repository, then use either the GitPython package or `subprocess` to extract the authors and commit dates.
My first development branch also displayed the commit description, but this information is not needed to calculate the on-hours / off-hours ratio.

The second step is to determine whether a commit was made off-hours (weekends or before 8 a.m. and after 8 p.m.).
The `weekday()` function can be used to identify weekdays, and the `hour` attribute of a datetime object gives the time.

The third step is to calculate the ratio of off-hours commits relative to the total number of commits.
In practice, using a `defaultdict` turned out to be useful for incrementing a list when the key does not yet exist.
The problem with this ratio is that it is not very meaningful for contributors with very few commits: for example, a contributor with only one off-hours commit would end up with a ratio of 100%.

To make the score more meaningful, we can compute an index based on the global average number of off-hours commits:

```txt
Index = Off-hours commits / Global average of off-hours commits
```
This index helps position a contributor’s off-hours activity relative to the average.
The final results table is sorted in descending order based on this index.

We can go further by taking into account the variation of the results by computing the standard deviation of the number of off-hours commits.
The standard deviation is calculated as the square root of the mean of the squared differences from the global average.


## Étapes de programmation

La première étape consiste à récupérer les commits du repository cible `passerelle`.  
Pour cela, il faut d'abord cloner le repository, puis utiliser soit le package GitPython, soit `subprocess` pour isoler les auteurs et les dates de chaque commit.  
Ma première branche de développement affichait également la description, mais cette information n'est pas utile pour calculer le ratio hors horaires / horaires.

La seconde étape consiste à déterminer si un commit est hors horaires (weekend ou avant 8h et après 20h).  
Il existe la fonction `weekday()` pour isoler les jours de la semaine et l'attribut `hour` pour obtenir l'heure d'un datetime.

La troisième étape consiste à calculer le ratio de commits hors horaires par rapport au nombre total de commits.  
Techniquement, l'utilisation d'un `defaultdict` s'est avérée utile pour incrémenter une liste dont la clé n'existe pas encore.
Le problème de ce ratio est qu'il n'est pas très significatif pour une personne ayant très peu contribué au projet : par exemple, un contributeur ayant effectué un seul commit hors horaires aurait un ratio de 100 %.  

Pour rendre le score plus significatif, on peut calculer un indice basé sur la moyenne globale des commits hors horaires :  

```txt
Indice = Commits hors horaires / Moyenne globale des commits hors horaires
```
Cet indice permet de situer l'activité hors horaires d'un contributeur par rapport à la moyenne.
Le tableau final des résulats est d'ailleurs trié par ordre décroissant selon cet indice.

On peut aller plus loin en tenant compte de la variation des résultats en calculant l'écart type du nombre de commits hors horaires.  
L'écart type se calcule comme la racine carrée de la moyenne des carrés des écarts par rapport à la moyenne globale.
