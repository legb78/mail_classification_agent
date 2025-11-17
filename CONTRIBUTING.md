# Guide de Contribution

Merci de votre intérêt pour contribuer à ce projet ! Ce document fournit des directives pour contribuer.

## Comment contribuer

### Signaler un bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](https://github.com/your-repo/issues)
2. Créez une nouvelle issue avec :
   - Un titre clair et descriptif
   - Une description détaillée du problème
   - Les étapes pour reproduire
   - Le comportement attendu vs. réel
   - Votre environnement (OS, Python version, etc.)

### Proposer une fonctionnalité

1. Vérifiez que la fonctionnalité n'a pas déjà été proposée
2. Créez une issue avec :
   - Une description claire de la fonctionnalité
   - Le cas d'usage
   - Les avantages potentiels

### Soumettre du code

1. Fork le repository
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Push vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

## Standards de code

### Style de code

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez `black` pour le formatage
- Utilisez `flake8` pour le linting
- Maximum 100 caractères par ligne

### Tests

- Écrivez des tests pour toute nouvelle fonctionnalité
- Assurez-vous que tous les tests passent
- Maintenez une couverture de code > 80%

### Documentation

- Documentez toutes les fonctions publiques
- Ajoutez des docstrings au format Google
- Mettez à jour le README si nécessaire

## Processus de revue

1. Toutes les PR seront revues par au moins un mainteneur
2. Les commentaires doivent être adressés avant le merge
3. Les tests doivent passer sur CI/CD
4. Le code doit respecter les standards

## Questions ?

N'hésitez pas à ouvrir une issue pour toute question !

