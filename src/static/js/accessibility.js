/**
 * Amélioration de l'accessibilité pour l'application JPJR
 * Ce fichier contient des correctifs et améliorations pour l'accessibilité de l'application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Correction du problème de focus pour les modals Bootstrap
    setupModalAccessibility();
});

/**
 * Améliore l'accessibilité des modals en gérant correctement le focus
 * Résout le problème "Blocked aria-hidden on an element because its descendant retained focus"
 */
function setupModalAccessibility() {
    // Pour chaque modal dans l'application
    document.querySelectorAll('.modal').forEach(modal => {
        // Quand un modal est sur le point d'être caché
        modal.addEventListener('hide.bs.modal', function() {
            // Transférer le focus à un élément sûr avant de cacher le modal
            const activeElement = document.activeElement;
            if (modal.contains(activeElement)) {
                // Trouver un élément externe pour recevoir le focus
                // Généralement le bouton qui a ouvert le modal ou le corps du document
                const triggerId = modal.getAttribute('data-bs-triggered-by');
                const trigger = triggerId ? document.getElementById(triggerId) : document.body;
                
                // Stocker temporairement le cible du focus dans un attribut de données
                modal.dataset.focusTarget = triggerId || 'body';
                
                // Retirer le focus de l'élément actif
                activeElement.blur();
            }
        });
        
        // Quand un modal est complètement caché
        modal.addEventListener('hidden.bs.modal', function() {
            // Restaurer le focus sur l'élément déclencheur ou le corps du document
            const focusTarget = modal.dataset.focusTarget === 'body' 
                ? document.body 
                : document.getElementById(modal.dataset.focusTarget);
                
            if (focusTarget) {
                // Pour le corps du document, nous définissons simplement tabIndex=-1 temporairement
                // pour pouvoir lui donner le focus
                if (focusTarget === document.body) {
                    document.body.setAttribute('tabindex', '-1');
                    document.body.focus();
                    document.body.removeAttribute('tabindex');
                } else {
                    focusTarget.focus();
                }
            }
            
            // Nettoyer l'attribut de données
            delete modal.dataset.focusTarget;
        });
    });
    
    // Marquer les boutons qui ouvrent des modals pour suivre le focus
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(button => {
        const targetId = button.getAttribute('data-bs-target') || button.getAttribute('href');
        if (targetId) {
            const modalId = targetId.replace('#', '');
            const modal = document.getElementById(modalId);
            if (modal) {
                // Stocker l'ID du bouton dans le modal
                modal.setAttribute('data-bs-triggered-by', button.id || '');
                
                // Si le bouton n'a pas d'ID, en générer un
                if (!button.id) {
                    button.id = 'modal-trigger-' + Math.random().toString(36).substr(2, 9);
                    modal.setAttribute('data-bs-triggered-by', button.id);
                }
            }
        }
    });
}
