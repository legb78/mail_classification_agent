"""
Classificateur de tickets utilisant Groq LLM
"""

import json
from typing import Dict
from groq import Groq
from src.utils.logger import get_logger
from src.utils.config import ClassificationConfig


class TicketClassifier:
    """
    Classificateur de tickets utilisant l'API Groq pour la classification intelligente
    """
    
    def __init__(self, config: ClassificationConfig):
        """
        Initialise le classificateur
        
        Args:
            config: Configuration de classification
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        if config.use_groq:
            if not config.groq_api_key:
                raise ValueError("GROQ_API_KEY est requis lorsque USE_GROQ_LLM=True")
            
            self.client = Groq(api_key=config.groq_api_key)
            self.model = config.groq_model
            self.logger.info(f"Classificateur Groq initialisé avec le modèle: {self.model}")
        else:
            self.client = None
            self.logger.warning("Groq LLM désactivé, utilisation du mode ML classique")
    
    def classify(self, subject: str, body: str, sender_email: str = "") -> Dict[str, any]:
        """
        Classe un ticket en fonction de son sujet et contenu
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email
            sender_email: Email de l'expéditeur (optionnel)
        
        Returns:
            Dictionnaire contenant:
            - category: Catégorie du ticket
            - priority: Priorité du ticket
            - confidence: Score de confiance (0-1)
            - reasoning: Raisonnement de la classification
        """
        if not self.config.use_groq or not self.client:
            return self._fallback_classification(subject, body)
        
        try:
            # Préparer le prompt pour Groq
            prompt = self._build_classification_prompt(subject, body, sender_email)
            
            # Appel à l'API Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Basse température pour plus de cohérence
                max_tokens=500,
                response_format={"type": "json_object"}  # Forcer la réponse JSON
            )
            
            # Parser la réponse JSON
            result = json.loads(response.choices[0].message.content)
            
            # Valider et normaliser la réponse
            category = self._validate_category(result.get("category", "Autre"))
            priority = self._validate_priority(result.get("priority", "Moyenne"))
            confidence = float(result.get("confidence", 0.8))
            reasoning = result.get("reasoning", "Classification effectuée par Groq LLM")
            
            self.logger.info(
                f"Ticket classifié - Catégorie: {category}, Priorité: {priority}, "
                f"Confiance: {confidence:.2f}"
            )
            
            return {
                "category": category,
                "priority": priority,
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Erreur de parsing JSON de la réponse Groq: {e}")
            return self._fallback_classification(subject, body)
        except Exception as e:
            self.logger.error(f"Erreur lors de la classification avec Groq: {e}")
            return self._fallback_classification(subject, body)
    
    def _build_classification_prompt(self, subject: str, body: str, sender_email: str) -> str:
        """
        Construit le prompt pour la classification
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email
            sender_email: Email de l'expéditeur
        
        Returns:
            Prompt formaté pour Groq
        """
        # Limiter la longueur du body pour éviter les tokens excessifs
        body_preview = body[:1000] if len(body) > 1000 else body
        
        prompt = f"""Analysez cet email de ticket et classez-le selon les critères suivants:

Sujet: {subject}
Expéditeur: {sender_email}
Contenu: {body_preview}

Catégories disponibles: {', '.join(self.config.categories)}
Priorités disponibles: {', '.join(self.config.priorities)}

Répondez au format JSON avec les champs suivants:
- "category": une des catégories disponibles
- "priority": une des priorités disponibles (Critique pour urgences, Haute pour problèmes importants, Moyenne pour demandes normales, Basse pour demandes non urgentes)
- "confidence": un score entre 0 et 1 indiquant votre confiance dans la classification
- "reasoning": une brève explication (1-2 phrases) de votre classification

Exemple de réponse:
{{
    "category": "Technique",
    "priority": "Haute",
    "confidence": 0.9,
    "reasoning": "Le ticket concerne un problème technique critique nécessitant une intervention rapide."
}}"""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """
        Retourne le prompt système pour guider le comportement du LLM
        
        Returns:
            Prompt système
        """
        return """Vous êtes un expert en classification de tickets de support. 
Votre rôle est d'analyser les emails entrants et de les classer avec précision selon leur catégorie et priorité.

Règles importantes:
- Analysez le contenu, le sujet et le contexte pour déterminer la catégorie
- Évaluez l'urgence et l'impact pour déterminer la priorité
- Utilisez "Critique" uniquement pour les problèmes bloquants ou urgents
- Soyez cohérent et objectif dans vos classifications
- Répondez toujours au format JSON valide"""
    
    def _validate_category(self, category: str) -> str:
        """
        Valide et normalise la catégorie
        
        Args:
            category: Catégorie proposée
        
        Returns:
            Catégorie validée
        """
        category_lower = category.lower().strip()
        
        # Mapping des variations possibles
        category_mapping = {
            "technique": "Technique",
            "technical": "Technique",
            "tech": "Technique",
            "commercial": "Commercial",
            "sales": "Commercial",
            "support": "Support",
            "facturation": "Facturation",
            "billing": "Facturation",
            "invoice": "Facturation",
            "autre": "Autre",
            "other": "Autre",
            "general": "Autre"
        }
        
        normalized = category_mapping.get(category_lower, category)
        
        if normalized not in self.config.categories:
            self.logger.warning(f"Catégorie '{normalized}' non reconnue, utilisation de 'Autre'")
            return "Autre"
        
        return normalized
    
    def _validate_priority(self, priority: str) -> str:
        """
        Valide et normalise la priorité
        
        Args:
            priority: Priorité proposée
        
        Returns:
            Priorité validée
        """
        priority_lower = priority.lower().strip()
        
        # Mapping des variations possibles
        priority_mapping = {
            "critique": "Critique",
            "critical": "Critique",
            "urgent": "Critique",
            "haute": "Haute",
            "high": "Haute",
            "moyenne": "Moyenne",
            "medium": "Moyenne",
            "normale": "Moyenne",
            "basse": "Basse",
            "low": "Basse"
        }
        
        normalized = priority_mapping.get(priority_lower, priority)
        
        if normalized not in self.config.priorities:
            self.logger.warning(f"Priorité '{normalized}' non reconnue, utilisation de 'Moyenne'")
            return "Moyenne"
        
        return normalized
    
    def _fallback_classification(self, subject: str, body: str) -> Dict[str, any]:
        """
        Classification de secours basée sur des règles simples
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email
        
        Returns:
            Classification basique
        """
        self.logger.warning("Utilisation de la classification de secours")
        
        text = f"{subject} {body}".lower()
        
        # Détection basique de catégorie
        if any(word in text for word in ["bug", "erreur", "erreur", "problème", "ne fonctionne pas", "crash"]):
            category = "Technique"
            priority = "Haute"
        elif any(word in text for word in ["achat", "vente", "devis", "prix", "commande"]):
            category = "Commercial"
            priority = "Moyenne"
        elif any(word in text for word in ["facture", "paiement", "facturation", "invoice"]):
            category = "Facturation"
            priority = "Moyenne"
        elif any(word in text for word in ["urgent", "critique", "bloquant", "immédiat"]):
            category = "Support"
            priority = "Critique"
        else:
            category = "Autre"
            priority = "Moyenne"
        
        return {
            "category": category,
            "priority": priority,
            "confidence": 0.5,
            "reasoning": "Classification basique basée sur des mots-clés (mode fallback)"
        }
    
    def extract_key_information(self, subject: str, body: str) -> Dict[str, any]:
        """
        Extrait des informations clés du ticket en utilisant Groq
        
        Args:
            subject: Sujet de l'email
            body: Corps de l'email
        
        Returns:
            Dictionnaire avec les informations extraites
        """
        if not self.config.use_groq or not self.client:
            return {}
        
        try:
            prompt = f"""Extrayez les informations clés de ce ticket:

Sujet: {subject}
Contenu: {body[:1500]}

Extrayez:
- Problème principal décrit
- Produit/service concerné (si mentionné)
- Numéro de référence ou ID (si présent)
- Action requise suggérée

Répondez au format JSON avec les champs:
- "main_issue": description du problème principal
- "product_service": produit/service concerné ou "N/A"
- "reference_number": numéro de référence ou "N/A"
- "suggested_action": action suggérée ou "N/A"
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un expert en extraction d'informations de tickets de support."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction d'informations: {e}")
            return {}

