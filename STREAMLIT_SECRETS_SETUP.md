# Configuration des Secrets Streamlit Cloud

## Problème
L'application affiche: `⚠️ Enrichissement INPI échoué: Client INPI non configuré (credentials manquants)`

## Solution

### Étape 1: Accéder aux paramètres de l'app

1. Connectez-vous à https://share.streamlit.io
2. Trouvez votre application "LOI-Bail-generateur" dans la liste
3. Cliquez sur les **3 points verticaux** (⋮) à droite de l'app
4. Sélectionnez **"Settings"**

### Étape 2: Configurer les Secrets

1. Dans le menu latéral gauche, cliquez sur **"Secrets"**
2. Dans l'éditeur qui apparaît, copiez-collez le contenu suivant:

```toml
INPI_USERNAME = "VOTRE_USERNAME_INPI"
INPI_PASSWORD = "VOTRE_PASSWORD_INPI"
```

3. **Remplacez** `VOTRE_USERNAME_INPI` et `VOTRE_PASSWORD_INPI` par vos vrais identifiants INPI
4. Cliquez sur **"Save"**

### Étape 3: Redémarrer l'application

1. L'application devrait redémarrer automatiquement
2. Si ce n'est pas le cas, cliquez sur **"Reboot"** dans les paramètres
3. Attendez quelques secondes que l'app redémarre

### Étape 4: Vérifier

1. Retournez sur votre application
2. Testez l'enrichissement avec un SIRET (par exemple: 532321916)
3. L'enrichissement INPI devrait maintenant fonctionner ✅

## Format des Secrets

**Important**: Les secrets utilisent le format TOML. Notez bien:
- Les valeurs doivent être **entre guillemets doubles** : `"valeur"`
- Pas d'espaces autour du `=`
- Une ligne par secret

### Exemple valide:
```toml
INPI_USERNAME = "mon_username"
INPI_PASSWORD = "mon_password123"
```

### ❌ Exemples invalides:
```toml
# INCORRECT - Pas de guillemets
INPI_USERNAME = mon_username

# INCORRECT - Guillemets simples
INPI_PASSWORD = 'mon_password'

# INCORRECT - Espaces autour du =
INPI_USERNAME = "mon_username"
```

## Sécurité

✅ **Les secrets sont:**
- Chiffrés par Streamlit Cloud
- Jamais visibles dans les logs
- Jamais exposés dans l'interface publique
- Accessibles uniquement par votre application

❌ **Ne jamais:**
- Commiter les secrets dans Git
- Partager vos credentials INPI publiquement
- Hardcoder les credentials dans le code

## Besoin d'aide?

Si l'enrichissement INPI ne fonctionne toujours pas après configuration:

1. Vérifiez que vos credentials INPI sont corrects
2. Vérifiez le format TOML (guillemets, pas d'espaces)
3. Vérifiez les logs de l'application dans Streamlit Cloud
4. Contactez le support si nécessaire
