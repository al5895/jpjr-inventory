// Utiliser le gestionnaire de notifications existant ou créer un fallback
if (typeof notificationManager === 'undefined') {
    // Fallback si notificationManager n'existe pas
    window.notificationManager = {
        success: function(message) {
            alert('Succès: ' + message);
        },
        error: function(message) {
            alert('Erreur: ' + message);
        },
        warning: function(message) {
            alert('Attention: ' + message);
        }
    };
}


// Fonction pour charger les emprunts existants
window.loadBorrows = async function() {
    const borrowsList = document.getElementById('borrowsList');
    
    try {
        appLog.log('Chargement des emprunts actifs...');
        // Vider la liste actuelle
        borrowsList.innerHTML = '<p class="text-center">Chargement des emprunts...</p>';
        
        // Récupérer les emprunts actifs
        const response = await fetch('/api/loans?active_only=true');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erreur HTTP ' + response.status);
        }
        
        const data = await response.json();
        appLog.log('Emprunts reçus (format brut):', data);
        
        // Vider la liste une fois les données reçues
        borrowsList.innerHTML = '';
        
        // Adapter la structure en fonction du format reçu
        let loans = [];
        if (Array.isArray(data)) {
            // Si la réponse est directement un tableau
            loans = data;
            appLog.log('Format détecté: tableau direct');
        } else if (data.loans && Array.isArray(data.loans)) {
            // Si la réponse est un objet avec une propriété loans
            loans = data.loans;
            appLog.log('Format détecté: objet avec propriété loans');
        } else {
            appLog.error('Format de réponse inattendu:', data);
            borrowsList.innerHTML = '<p class="text-center text-danger">Erreur: Format de données incorrect</p>';
            return;
        }
        
        appLog.log('Emprunts normalisés:', loans);
        
        // Si aucun emprunt actif
        if (loans.length === 0) {
            borrowsList.innerHTML = '<p class="text-center">Aucun emprunt en cours</p>';
            return;
        }
        
        // Parcourir les emprunts et les ajouter à la liste
        loans.forEach(loan => {
            // Cloner le template
            const template = document.getElementById('borrowTemplate');
            const clone = document.importNode(template.content, true);
            
            // Remplir les informations de l'emprunt
            const itemName = clone.querySelector('.item-name');
            const borrowDate = clone.querySelector('.borrow-date');
            const returnDate = clone.querySelector('.return-date');
            const returnButton = clone.querySelector('.return-item');
            const locationInfo = clone.querySelector('.location-info');
            
            itemName.textContent = loan.item_name;
            borrowDate.textContent = new Date(loan.borrow_date).toLocaleDateString('fr-FR');
            returnDate.textContent = loan.expected_return_date ? new Date(loan.expected_return_date).toLocaleDateString('fr-FR') : 'Non spécifiée';
            
            // Ajouter l'ID à l'élément pour le retour
            returnButton.dataset.borrowId = loan.id;
            
            // Ajouter les informations de localisation si disponibles
            if (loan.item_zone || loan.item_mobilier || loan.item_niveau_tiroir) {
                locationInfo.classList.remove('d-none');
                
                if (loan.item_zone) {
                    const zoneInfo = clone.querySelector('.zone-info');
                    zoneInfo.classList.remove('d-none');
                    zoneInfo.querySelector('span').textContent = loan.item_zone;
                }
                
                if (loan.item_mobilier) {
                    const mobilierInfo = clone.querySelector('.mobilier-info');
                    mobilierInfo.classList.remove('d-none');
                    mobilierInfo.querySelector('span').textContent = loan.item_mobilier;
                }
                
                if (loan.item_niveau_tiroir) {
                    const niveauInfo = clone.querySelector('.niveau-info');
                    niveauInfo.classList.remove('d-none');
                    niveauInfo.querySelector('span').textContent = loan.item_niveau_tiroir;
                }
            }
            
            // Ajouter le gestionnaire d'événement pour le retour
            returnButton.addEventListener('click', function() {
                handleReturn(this.dataset.borrowId, this);
            });
            
            borrowsList.appendChild(clone);
        });
    } catch (error) {
        appLog.error('Erreur:', error);
        notificationManager.error(error.message || 'Erreur lors du chargement des emprunts');
    }
}

// Fonction pour gérer le retour d'un article
window.handleReturn = async function(borrowId, button) {
    // Si le bouton est déjà en mode confirmation, procéder au retour
    if (button.classList.contains('confirming')) {
        try {
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split"></i> Traitement...';
            
            const response = await fetch(`/api/loans/${borrowId}/return`, {
                method: 'POST'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors du retour de l\'article');
            }
            
            // Retour réussi
            notificationManager.success('Article retourné avec succès');
            
            // Recharger la liste des emprunts
            loadBorrows();
        } catch (error) {
            appLog.error('Erreur:', error);
            notificationManager.error(error.message || 'Erreur lors du retour de l\'article');
            
            // Remettre le bouton dans son état initial
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-arrow-return-left"></i> Retourner';
            button.classList.remove('confirming');
        }
    } else {
        // Première étape : demander confirmation
        button.classList.add('confirming', 'btn-danger');
        button.classList.remove('btn-success');
        button.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Confirmer le retour';
        
        // Rétablir l'état initial après 3 secondes si pas de confirmation
        setTimeout(() => {
            if (button.classList.contains('confirming')) {
                button.classList.remove('confirming', 'btn-danger');
                button.classList.add('btn-success');
                button.innerHTML = '<i class="bi bi-arrow-return-left"></i> Retourner';
            }
        }, 3000);
    }
}
