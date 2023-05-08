# README du dossier "Executable"
Ce dossier contient toutes les ressources nécessaires pour démarrer ABVS chez vous et l'utilisez. Il y a donc le fichier main.exe pour démarrer le programme, le dossier "lib" et les fichiers "python3.dll" et "python311.dll" sont des fichiers ressources, et pour finir les dossiers "Datas" et "Backup" qui contiennent, comme leur nom l'indique, pour l'un les données sur lesquelles le programme se base et une sauvegarde de toutes les données sous des fichiers .txt. 
De plus, vous trouverez dans ce dossier le fichier "ABVS 0.1.zip" qui regroupe tout les autres fichiers du dossier dans un .zip pour vous faciliter le téléchargement.

Voici donc les instructions pour télécharger ABVS :
1. Téléchargez le fichier "ABVS 0.1.zip"
2. Une fois téléchargé, décompressez le (la destination des fichiers tient à vous).
3. Vous avez donc les fichiers nécessaires pour démarrer ABVS, pour connaître les étapes à suivre je vous renvoie vers le README principal, qui regroupe les deux README des sous-dossiers, ou directement le README du dossier "Source code" qui vous donne toutes les informations nécessaires.


# README du dossier "Source code"
## Bienvenue dans ABVS
### Comment démarrer ABVS
**Ne démarrez par ABVS maintenant, allez à la section [Démarrer ABVS pour la première fois](#Démarrer-ABVS-pour-la-première-fois)**

Pour démarrer ABVS, double-clickez sur le fichier "main.exe". Un invité de commandes s'ouvrira. Dans cette fenêtre, vous trouverez tous les logs liés à votre utilisation d'ABVS : quelles abréviations ont été rajoutées, supprimées, si les données ont été sauvegardées, etc... Ces informations seront ensuite enregistrées dans le fichier "log.txt" dans le dossier Data. 

#### Pro tip
Pour ne pas avoir à lancer ABVS de cette manière à chaque fois, il est conseillé de mettre en place 2 choses :
###### Créez un raccourci du fichier "main.exe" sur votre bureau puis ajoutez-lui une touche de raccourci 
Pour ce faire :
1. Faites un **clic droit sur le fichier**, **mettez votre souris sur la ligne "Envoyez vers"** puis **clickez sur "Bureau (créer un raccourci)"**. Vous êtes ensuite libre de renommer le fichier sur votre bureau.
2. Faites un **clic droit sur le raccourci** sur votre bureau, **clickez sur "Propriétés"** puis **rentrez la touche de raccourci** qui vous convient le mieux dans l'encadré "Touche de raccourci". Sachez que **"CTRL + ALT" est équivalent à la touche "AltGr"** de votre clavier. Si vous mettez donc la touche "s" en raccourci, vous pourrez donc appuyer sur \[AltGr\] + \[S\] pour démarrer ABVS. Il est aussi recommandé de **mettre l'option Exécuter sur "Réduite"** pour que la fenêtre ne s'ouvre pas en premier plan. 

###### Créez un raccourci du fichier "run.bat" dans votre dossier de démarrage
Puisque ce programme fonctionne en arrière-plan (et que je n'ai toujours pas trouvé de manière de le faire tourner en arrière-plan automatiquement), le mieux serait de le démarrer automatiquement au démarrage de votre ordinateur. Vous pouvez démarrer un programme au démarrage de votre ordinateur en mettant un raccourci de ce programme dans un certain dossier de votre ordinateur.Voici les étapes pour le faire :
1. **Appuyez sur \[Windows\] + \[R\]** puis **rentrez "shell:startup"** dans la fenêtre. Vous voici dans le fameux dossier.
2. Retournez dans le dossier ABVS, **faites un clic-droit sur le fichier "run.bat"** et **cliquez sur "Créer un raccourci"**
3. Ensuite, **déplacer le raccourci créé dans le dossier Démarrage** ouvert à la première étape.

Vous venez de créer un raccourci de ABVS sur votre bureau et de faire en sortes que ABVS démarre automatiquement au démarrage de Windows.

### Démarrer ABVS pour la première fois
Maintenant que vous venez de mettre en place des démarrages faciles et automatiques. La seule interface d'ABVS est la liste des logs qui a été évoquée plus haut, vous communiquerez donc avec ABVS par du texte écrit. Pour comprendre, ouvrez un fichier texte et démarrez ABVS. Si vous regardez la fenêtre ouverte, il devrait y avoir écrit "ABVS est démarré". Dans votre fichier texte, appuyez sur les touches 'abv_' en même temps. Il est vivement conseillé de suivre le tutoriel, même s'il n'est pas indispensable pour comprendre comment fonctionne ABVS.