"""
Groq Agent Module

Handles Groq API calls for email classification, urgency detection, and summary generation.
"""

import json
import logging
import time
from typing import Dict, List, Optional
from groq import Groq

logger = logging.getLogger(__name__)

# Category mapping (French to sheet names)
# Each category will be a separate sheet in Google Sheets
CATEGORIES = [
    "Technique",
    "Administratif",
    "Accès/Authentification",
    "Support utilisateur",
    "Bug/Dysfonctionnement"
]

URGENCY_LEVELS = [
    "Critique",
    "Élevée",
    "Modérée",
    "Faible",
    "Anodine"
]


class GroqAgent:
    """Handles Groq API operations for email analysis."""
    
    def __init__(self, api_key: str, model: str = "qwen/qwen3-32b"):
        """
        Initialize Groq Agent.
        
        Args:
            api_key: Groq API key
            model: Groq model to use (default: llama-3.1-8b-instant)
        """
        self.api_key = api_key
        self.model = model
        self.client = Groq(api_key=api_key)
        
    def analyze_email(self, subject: str, body: str) -> Dict[str, str]:
        """
        Analyze an email and return classification, urgency, and summary.
        
        Args:
            subject: Email subject
            body: Email body text
            
        Returns:
            Dictionary with 'categorie', 'urgence', 'synthese'
        """
        try:
            # Prepare prompt
            prompt = self._create_analysis_prompt(subject, body)
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un assistant expert en classification de tickets e-mail. Tu réponds UNIQUEMENT en JSON valide, sans texte supplémentaire."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            # Extract JSON from response
            content = response.choices[0].message.content
            result = json.loads(content)
            
            # Validate and normalize result
            result = self._validate_result(result)
            
            logger.debug(f"Analyzed email: {subject[:50]}... -> {result['categorie']}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            try:
                content = response.choices[0].message.content
                logger.error(f"Response content: {content[:200]}")
            except:
                pass
            return self._get_fallback_result(subject, body)
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            return self._get_fallback_result(subject, body)
    
    def analyze_batch(self, emails: List[Dict[str, str]], batch_size: int = 20) -> List[Dict[str, str]]:
        """
        Analyze multiple emails in batches.
        
        Args:
            emails: List of email dictionaries with 'subject' and 'body'
            batch_size: Number of emails to process per batch
            
        Returns:
            List of analysis results
        """
        results = []
        total = len(emails)
        
        for i in range(0, total, batch_size):
            batch = emails[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} emails)")
            
            batch_results = []
            for email in batch:
                try:
                    result = self.analyze_email(email['subject'], email['body'])
                    result['email_id'] = email.get('id')
                    batch_results.append(result)
                    # Small delay to respect rate limits
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error processing email {email.get('id', 'unknown')}: {str(e)}")
                    fallback = self._get_fallback_result(email['subject'], email['body'])
                    fallback['email_id'] = email.get('id')
                    batch_results.append(fallback)
            
            results.extend(batch_results)
            
            # Delay between batches
            if i + batch_size < total:
                time.sleep(1)
        
        return results
    
    def _create_analysis_prompt(self, subject: str, body: str) -> str:
        """Create the analysis prompt for Groq."""
        prompt = f"""Analyse ce ticket e-mail et réponds en JSON avec exactement ces clés:
- "categorie": une des catégories suivantes: {', '.join(CATEGORIES)}
- "urgence": un des niveaux suivants: {', '.join(URGENCY_LEVELS)}
- "synthese": un résumé court de 2-3 lignes en français

Sujet: {subject}

Corps:
{body[:2000]}

Réponds UNIQUEMENT avec un objet JSON valide, sans texte supplémentaire."""
        return prompt
    
    def _validate_result(self, result: Dict) -> Dict[str, str]:
        """
        Validate and normalize the Groq response.
        
        Args:
            result: Raw result dictionary
            
        Returns:
            Validated result dictionary
        """
        validated = {
            'categorie': result.get('categorie', 'Support utilisateur'),
            'urgence': result.get('urgence', 'Modérée'),
            'synthese': result.get('synthese', 'Synthèse non disponible')
        }
        
        # Normalize category
        categorie = validated['categorie']
        if categorie not in CATEGORIES:
            # Try to find closest match
            categorie_lower = categorie.lower()
            for cat in CATEGORIES:
                if cat.lower() in categorie_lower or categorie_lower in cat.lower():
                    validated['categorie'] = cat
                    break
            else:
                validated['categorie'] = 'Support utilisateur'
                logger.warning(f"Unknown category '{categorie}', defaulting to 'Support utilisateur'")
        
        # Normalize urgency
        urgence = validated['urgence']
        if urgence not in URGENCY_LEVELS:
            urgence_lower = urgence.lower()
            for level in URGENCY_LEVELS:
                if level.lower() in urgence_lower or urgence_lower in level.lower():
                    validated['urgence'] = level
                    break
            else:
                validated['urgence'] = 'Modérée'
                logger.warning(f"Unknown urgency '{urgence}', defaulting to 'Modérée'")
        
        # Ensure summary is not empty
        if not validated['synthese'] or len(validated['synthese'].strip()) == 0:
            validated['synthese'] = 'Synthèse non disponible'
        
        return validated
    
    def _get_fallback_result(self, subject: str, body: str) -> Dict[str, str]:
        """
        Get a fallback result when API call fails.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Fallback result dictionary
        """
        logger.warning("Using fallback classification")
        
        # Simple keyword-based fallback
        text = (subject + " " + body).lower()
        
        # Determine category
        if any(word in text for word in ['bug', 'erreur', 'dysfonctionnement', 'ne fonctionne pas', 'crash']):
            categorie = 'Bug/Dysfonctionnement'
        elif any(word in text for word in ['accès', 'authentification', 'login', 'mot de passe', 'compte']):
            categorie = 'Accès/Authentification'
        elif any(word in text for word in ['technique', 'technologie', 'serveur', 'api', 'code']):
            categorie = 'Technique'
        elif any(word in text for word in ['administratif', 'facture', 'paiement', 'contrat']):
            categorie = 'Administratif'
        else:
            categorie = 'Support utilisateur'
        
        # Determine urgency
        if any(word in text for word in ['urgent', 'critique', 'bloquant', 'immédiat']):
            urgence = 'Critique'
        elif any(word in text for word in ['important', 'priorité', 'rapide']):
            urgence = 'Élevée'
        elif any(word in text for word in ['pas urgent', 'quand possible', 'anodin']):
            urgence = 'Anodine'
        else:
            urgence = 'Modérée'
        
        # Simple summary
        synthese = f"Ticket concernant: {subject}. {body[:100]}..." if len(body) > 100 else f"Ticket: {subject}"
        
        return {
            'categorie': categorie,
            'urgence': urgence,
            'synthese': synthese
        }

