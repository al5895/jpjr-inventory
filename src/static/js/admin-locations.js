/**
 * admin-locations.js
 * Script pour la page d'administration des emplacements
 * Utilise location-core.js comme bibliothèque de base
 */

// Variables globales pour stocker les données actuelles
let currentZoneId = null;
let currentFurnitureId = null;

document.addEventListener('DOMContentLoaded', function() {
    // Vérifier si nous sommes sur la page d'administration des emplacements
    if (!document.getElementById('locationManager')) {
        return;
    }
    
    appLog.log('Page d\'administration des emplacements détectée');
    
    // Vérifier si Bootstrap est disponible
    if (typeof bootstrap === 'undefined') {
        appLog.error('Bootstrap n\'est pas chargé. Les fonctionnalités modales ne fonctionneront pas correctement.');
        // On continue quand même l'initialisation avec un message d'erreur
        const container = document.querySelector('.container');
        if (container) {
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger';
            alertDiv.innerHTML = '<strong>Erreur:</strong> La bibliothèque Bootstrap n\'est pas chargée correctement. Certaines fonctionnalités pourraient ne pas fonctionner.';
            container.prepend(alertDiv);
        }
    }
    
    // Initialiser tous les composants
    initZonesPanel();
    initModals();
    initDeleteConfirmation();
    
    // Ajouter des gestionnaires d'événements aux boutons dynamiquement ajoutés
    document.addEventListener('click', function(event) {
        // Délégation d'événements pour les boutons qui pourraient être ajoutés dynamiquement
        if (event.target.closest('.view-zone-furniture')) {
            const btn = event.target.closest('.view-zone-furniture');
            const zoneId = btn.getAttribute('data-id');
            const zoneName = btn.getAttribute('data-name');
            loadFurnitureForZone(zoneId, zoneName);
            event.preventDefault();
        }
    });
    
});

/**
 * Initialiser le panneau des zones et les événements associés
 */
function initZonesPanel() {
    appLog.log('Initialisation du panneau des zones');
    
    // Événements pour les zones
    document.querySelectorAll('.view-zone-furniture').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Empêcher le comportement par défaut
            const zoneId = this.getAttribute('data-id');
            const zoneName = this.getAttribute('data-name');
            appLog.log('Chargement des meubles pour la zone:', zoneName);
            loadFurnitureForZone(zoneId, zoneName);
        });
    });

    document.querySelectorAll('.edit-zone').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Empêcher le comportement par défaut
            const zoneId = this.getAttribute('data-id');
            const zoneName = this.getAttribute('data-name');
            appLog.log('Ouverture modal d\'édition de zone:', zoneName);
            showZoneModal('edit', zoneId, zoneName);
        });
    });

    document.querySelectorAll('.delete-zone, .delete-zone-tree').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Empêcher le comportement par défaut
            const zoneId = this.getAttribute('data-id');
            const zoneName = this.getAttribute('data-name');
            appLog.log('Confirmation de suppression de zone:', zoneName);
            showDeleteConfirmation('zone', zoneId, zoneName);
        });
    });

    document.querySelectorAll('.add-furniture, .add-furniture-tree').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Empêcher le comportement par défaut
            const zoneId = this.getAttribute('data-zone-id');
            const zoneName = this.getAttribute('data-zone-name');
            appLog.log('Ouverture modal d\'ajout de meuble pour la zone:', zoneName);
            showFurnitureModal('add', null, zoneId, zoneName);
        });
    });

    // Bouton d'ajout de zone
    const addZoneBtn = document.getElementById('addZoneBtn');
    if (addZoneBtn) {
        addZoneBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Empêcher le comportement par défaut
            appLog.log('Ouverture modal d\'ajout de zone');
            showZoneModal('add');
        });
    } else {
        appLog.error('Bouton d\'ajout de zone non trouvé');
    }
}

/**
 * Charger les meubles pour une zone spécifique
 */
function loadFurnitureForZone(zoneId, zoneName) {
    currentZoneId = zoneId;
    
    // Mettre à jour l'interface
    document.getElementById('selectedZoneName').textContent = zoneName;
    
    // Récupérer les meubles de cette zone
    fetch(`/api/location/furniture?zone_id=${zoneId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des meubles');
            }
            return response.json();
        })
        .then(furniture => {
            renderFurnitureList(furniture, zoneId, zoneName);
        })
        .catch(error => {
            notificationManager.error(error.message);
        });
}

/**
 * Afficher les meubles dans la liste
 */
function renderFurnitureList(furniture, zoneId, zoneName) {
    const container = document.getElementById('furnitureContainer');
    if (!furniture || furniture.length === 0) {
        container.innerHTML = `
            <div class="empty-message">Aucun meuble dans cette zone</div>
            <div class="add-button-container text-center">
                <button class="btn btn-success add-furniture" data-zone-id="${zoneId}" data-zone-name="${zoneName}">
                    <i class="bi bi-plus-lg"></i> Ajouter un meuble
                </button>
            </div>
        `;
        
        // Ajouter l'événement au nouveau bouton
        container.querySelector('.add-furniture').addEventListener('click', function() {
            showFurnitureModal('add', null, zoneId, zoneName);
        });
        return;
    }
    
    // Créer la liste des meubles
    let html = `<div class="list-group list-group-flush" id="furnitureList">`;
    
    furniture.forEach(item => {
        html += `
        <div class="list-group-item d-flex justify-content-between align-items-center" 
             data-id="${item.id}" data-name="${item.name}">
            <div>
                <span class="fw-bold text-success">${item.name}</span>
                <small class="text-muted d-block">${item.drawers ? item.drawers.length : 0} tiroir(s)</small>
            </div>
            <div class="btn-group">
                <button class="btn btn-outline-primary btn-sm view-furniture-drawers" 
                        data-id="${item.id}" data-name="${item.name}">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm add-drawer" 
                        data-furniture-id="${item.id}" data-furniture-name="${item.name}">
                    <i class="bi bi-plus-lg"></i> Tiroir
                </button>
                <button class="btn btn-outline-secondary btn-sm edit-furniture" 
                        data-id="${item.id}" data-name="${item.name}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm delete-furniture" 
                        data-id="${item.id}" data-name="${item.name}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
        `;
    });
    
    html += `</div>
    <div class="add-button-container text-center">
        <button class="btn btn-success add-furniture" data-zone-id="${zoneId}" data-zone-name="${zoneName}">
            <i class="bi bi-plus-lg"></i> Ajouter un meuble
        </button>
    </div>`;
    
    container.innerHTML = html;
    
    // Ajouter les événements aux nouveaux boutons
    container.querySelectorAll('.view-furniture-drawers').forEach(btn => {
        btn.addEventListener('click', function() {
            const furnitureId = this.getAttribute('data-id');
            const furnitureName = this.getAttribute('data-name');
            loadDrawersForFurniture(furnitureId, furnitureName);
        });
    });
    
    container.querySelectorAll('.edit-furniture').forEach(btn => {
        btn.addEventListener('click', function() {
            const furnitureId = this.getAttribute('data-id');
            const furnitureName = this.getAttribute('data-name');
            showFurnitureModal('edit', furnitureId, currentZoneId, zoneName);
        });
    });
    
    container.querySelectorAll('.delete-furniture').forEach(btn => {
        btn.addEventListener('click', function() {
            const furnitureId = this.getAttribute('data-id');
            const furnitureName = this.getAttribute('data-name');
            showDeleteConfirmation('furniture', furnitureId, furnitureName);
        });
    });
    
    container.querySelectorAll('.add-drawer').forEach(btn => {
        btn.addEventListener('click', function() {
            const furnitureId = this.getAttribute('data-furniture-id');
            const furnitureName = this.getAttribute('data-furniture-name');
            showDrawerModal('add', null, furnitureId, furnitureName);
        });
    });
    
    container.querySelector('.add-furniture').addEventListener('click', function() {
        showFurnitureModal('add', null, zoneId, zoneName);
    });
}

/**
 * Charger les tiroirs pour un meuble spécifique
 */
function loadDrawersForFurniture(furnitureId, furnitureName) {
    currentFurnitureId = furnitureId;
    
    // Mettre à jour l'interface
    document.getElementById('selectedFurnitureName').textContent = furnitureName;
    
    // Récupérer les tiroirs de ce meuble
    fetch(`/api/location/drawers?furniture_id=${furnitureId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des tiroirs');
            }
            return response.json();
        })
        .then(drawers => {
            renderDrawersList(drawers, furnitureId, furnitureName);
        })
        .catch(error => {
            notificationManager.error(error.message);
        });
}

/**
 * Afficher les tiroirs dans la liste
 */
function renderDrawersList(drawers, furnitureId, furnitureName) {
    const container = document.getElementById('drawerContainer');
    if (!drawers || drawers.length === 0) {
        container.innerHTML = `
            <div class="empty-message">Aucun tiroir dans ce meuble</div>
            <div class="add-button-container text-center">
                <button class="btn btn-danger add-drawer" data-furniture-id="${furnitureId}" data-furniture-name="${furnitureName}">
                    <i class="bi bi-plus-lg"></i> Ajouter un tiroir/niveau
                </button>
            </div>
        `;
        
        // Ajouter l'événement au nouveau bouton
        container.querySelector('.add-drawer').addEventListener('click', function() {
            showDrawerModal('add', null, furnitureId, furnitureName);
        });
        return;
    }
    
    // Créer la liste des tiroirs
    let html = `<div class="list-group list-group-flush" id="drawersList">`;
    
    drawers.forEach(item => {
        html += `
        <div class="list-group-item d-flex justify-content-between align-items-center" 
             data-id="${item.id}" data-name="${item.name}">
            <div>
                <span class="fw-bold text-danger">${item.name}</span>
                <small class="text-muted d-block">${item.description || ''}</small>
            </div>
            <div class="btn-group">
                <button class="btn btn-outline-secondary btn-sm edit-drawer" 
                        data-id="${item.id}" data-name="${item.name}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-outline-danger btn-sm delete-drawer" 
                        data-id="${item.id}" data-name="${item.name}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
        `;
    });
    
    html += `</div>
    <div class="add-button-container text-center">
        <button class="btn btn-danger add-drawer" data-furniture-id="${furnitureId}" data-furniture-name="${furnitureName}">
            <i class="bi bi-plus-lg"></i> Ajouter un tiroir/niveau
        </button>
    </div>`;
    
    container.innerHTML = html;
    
    // Ajouter les événements aux nouveaux boutons
    container.querySelectorAll('.edit-drawer').forEach(btn => {
        btn.addEventListener('click', function() {
            const drawerId = this.getAttribute('data-id');
            const drawerName = this.getAttribute('data-name');
            showDrawerModal('edit', drawerId, currentFurnitureId, furnitureName);
        });
    });
    
    container.querySelectorAll('.delete-drawer').forEach(btn => {
        btn.addEventListener('click', function() {
            const drawerId = this.getAttribute('data-id');
            const drawerName = this.getAttribute('data-name');
            showDeleteConfirmation('drawer', drawerId, drawerName);
        });
    });
    
    container.querySelector('.add-drawer').addEventListener('click', function() {
        showDrawerModal('add', null, furnitureId, furnitureName);
    });
}

/**
 * Initialiser les modales
 */
function initModals() {
    // Modal de zone
    document.getElementById('saveZone').addEventListener('click', function() {
        saveZone();
    });
    
    // Modal de meuble
    document.getElementById('saveFurniture').addEventListener('click', function() {
        saveFurniture();
    });
    
    // Modal de tiroir
    document.getElementById('saveDrawer').addEventListener('click', function() {
        saveDrawer();
    });
    
    // Ajouter les événements aux boutons d'ajout de tiroirs dans la vue arborescente
    document.querySelectorAll('.add-drawer-tree').forEach(btn => {
        btn.addEventListener('click', function() {
            const furnitureId = this.getAttribute('data-furniture-id');
            const furnitureName = this.getAttribute('data-furniture-name');
            showDrawerModal('add', null, furnitureId, furnitureName);
        });
    });
    
    // Ajouter les événements aux boutons de suppression dans la vue arborescente
    document.querySelectorAll('.delete-furniture-tree').forEach(btn => {
        btn.addEventListener('click', function() {
            const furnitureId = this.getAttribute('data-id');
            const furnitureName = this.getAttribute('data-name');
            showDeleteConfirmation('furniture', furnitureId, furnitureName);
        });
    });
    
    document.querySelectorAll('.delete-drawer-tree').forEach(btn => {
        btn.addEventListener('click', function() {
            const drawerId = this.getAttribute('data-id');
            const drawerName = this.getAttribute('data-name');
            showDeleteConfirmation('drawer', drawerId, drawerName);
        });
    });
}

/**
 * Initialiser la modale de confirmation de suppression
 */
function initDeleteConfirmation() {
    const deleteModal = document.getElementById('deleteModal');
    if (!deleteModal) return;
    
    document.getElementById('confirmDelete').addEventListener('click', function() {
        const type = document.getElementById('deleteType').value;
        const id = document.getElementById('deleteId').value;
        deleteLocationItem(type, id);
    });
}

/**
 * Afficher la modale de confirmation de suppression
 */
function showDeleteConfirmation(type, id, name) {
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    
    document.getElementById('deleteType').value = type;
    document.getElementById('deleteId').value = id;
    
    let message = '';
    let warning = '';
    
    switch (type) {
        case 'zone':
            message = `Êtes-vous sûr de vouloir supprimer la zone "${name}" ?`;
            warning = 'Cette action supprimera également tous les meubles et tiroirs associés à cette zone.';
            break;
        case 'furniture':
            message = `Êtes-vous sûr de vouloir supprimer le meuble "${name}" ?`;
            warning = 'Cette action supprimera également tous les tiroirs associés à ce meuble.';
            break;
        case 'drawer':
            message = `Êtes-vous sûr de vouloir supprimer le tiroir/niveau "${name}" ?`;
            warning = 'Les articles associés à ce tiroir deviendront inaccessibles jusqu\'à ce qu\'ils soient réassignés.';
            break;
    }
    
    document.getElementById('deleteMessage').textContent = message;
    document.getElementById('deleteWarning').textContent = warning;
    
    deleteModal.show();
}

/**
 * Supprimer un élément de location
 */
function deleteLocationItem(type, id) {
    LocationCore.deleteLocationItem(type, id)
        .then(success => {
            // LocationCore.deleteLocationItem résout avec true en cas de succès,
            // ou lève une erreur qui sera attrapée par .catch().
            const itemTypeFrench = type === 'zone' ? 'Zone' : type === 'furniture' ? 'Meuble' : 'Tiroir';
            notificationManager.success(`${itemTypeFrench} supprimé(e) avec succès`);
            
            const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            if (deleteModal) {
                deleteModal.hide();
            }
            
            setTimeout(() => {
                window.location.reload();
            }, 500);
        })
        .catch(error => {
            notificationManager.error(error.message || 'Erreur inconnue lors de la suppression.');
        });
}

/**
 * Afficher la modale de zone (ajout ou édition)
 */
function showZoneModal(mode, zoneId = null, zoneName = '') {
    try {
        appLog.log('Ouverture de la modale de zone:', mode, zoneId, zoneName);
        
        // Sélectionner la modale
        const zoneModalElement = document.getElementById('zoneModal');
        if (!zoneModalElement) {
            appLog.error('Modal zone non trouvé');
            return;
        }
        
        // Mise à jour des champs
        const titleElement = document.getElementById('zoneModalTitle');
        if (titleElement) {
            titleElement.textContent = mode === 'add' ? 'Ajouter une zone' : 'Modifier la zone';
        }
        
        const idElement = document.getElementById('zoneId');
        if (idElement) {
            idElement.value = zoneId || '';
        }
        
        const nameElement = document.getElementById('zoneName');
        if (nameElement) {
            nameElement.value = zoneName || '';
        }
        
        const descElement = document.getElementById('zoneDescription');
        if (descElement) {
            descElement.value = '';
        }
        
        // Initialiser et afficher la modale
        let zoneModal;
        if (typeof bootstrap !== 'undefined') {
            zoneModal = new bootstrap.Modal(zoneModalElement);
            zoneModal.show();
        } else {
            // Fallback si bootstrap n'est pas disponible
            appLog.error('Bootstrap non disponible');
            zoneModalElement.style.display = 'block';
            zoneModalElement.classList.add('show');
        }
    } catch (error) {
        appLog.error('Erreur lors de l\'ouverture de la modale de zone:', error);
        notificationManager.error('Erreur lors de l\'ouverture de la modale');
    }
}

/**
 * Enregistrer une zone (création ou modification)
 */
function saveZone() {
    const zoneId = document.getElementById('zoneId').value;
    const name = document.getElementById('zoneName').value;
    const description = document.getElementById('zoneDescription').value;
    
    if (!name.trim()) {
        notificationManager.warning('Le nom de la zone ne peut pas être vide');
        return;
    }
    
    const isEdit = zoneId !== '';
    let promise;
    if (isEdit) {
        promise = LocationCore.updateLocationItem('zone', zoneId, { name, description });
    } else {
        promise = LocationCore.createZone(name, description);
    }

    promise
    .then(data => {
        notificationManager.success('Zone enregistrée avec succès');
        
        // Fermer le modal
        const zoneModal = bootstrap.Modal.getInstance(document.getElementById('zoneModal'));
        zoneModal.hide();
        
        // Recharger la page
        setTimeout(() => window.location.reload(), 500);
    })
    .catch(error => {
        notificationManager.error(error.message);
    });
}

/**
 * Afficher la modale de meuble (ajout ou édition)
 */
function showFurnitureModal(mode, furnitureId = null, zoneId, zoneName) {
    const furnitureModal = new bootstrap.Modal(document.getElementById('furnitureModal'));
    
    // Mise à jour des champs
    document.getElementById('furnitureModalTitle').textContent = mode === 'add' ? 'Ajouter un meuble' : 'Modifier le meuble';
    document.getElementById('furnitureId').value = furnitureId || '';
    document.getElementById('furnitureName').value = furnitureId ? document.querySelector(`.list-group-item[data-id="${furnitureId}"] .fw-bold`).textContent : '';
    document.getElementById('furnitureDescription').value = '';
    document.getElementById('furnitureZoneId').value = zoneId;
    document.getElementById('furnitureZoneName').value = zoneName;
    
    furnitureModal.show();
}

/**
 * Enregistrer un meuble (création ou modification)
 */
function saveFurniture() {
    const furnitureId = document.getElementById('furnitureId').value;
    const name = document.getElementById('furnitureName').value;
    const description = document.getElementById('furnitureDescription').value;
    const zoneId = document.getElementById('furnitureZoneId').value;
    
    if (!name.trim()) {
        notificationManager.warning('Le nom du meuble ne peut pas être vide');
        return;
    }
    
    if (!zoneId) {
        notificationManager.warning('Une zone doit être sélectionnée');
        return;
    }
    
    const isEdit = furnitureId !== '';
    let promise;
    if (isEdit) {
        promise = LocationCore.updateLocationItem('furniture', furnitureId, { name, description, zone_id: zoneId });
    } else {
        promise = LocationCore.createFurniture(zoneId, name, description);
    }

    promise
    .then(data => {
        notificationManager.success('Meuble enregistré avec succès');
        
        // Fermer le modal
        const furnitureModal = bootstrap.Modal.getInstance(document.getElementById('furnitureModal'));
        furnitureModal.hide();
        
        // Si nous sommes en train de visualiser la zone concernée, recharger juste les meubles
        if (currentZoneId === zoneId) {
            loadFurnitureForZone(zoneId, document.getElementById('furnitureZoneName').value);
        } else {
            // Sinon recharger la page
            setTimeout(() => window.location.reload(), 500);
        }
    })
    .catch(error => {
        notificationManager.error(error.message);
    });
}

/**
 * Afficher la modale de tiroir (ajout ou édition)
 */
function showDrawerModal(mode, drawerId = null, furnitureId, furnitureName) {
    const drawerModal = new bootstrap.Modal(document.getElementById('drawerModal'));
    
    // Mise à jour des champs
    document.getElementById('drawerModalTitle').textContent = mode === 'add' ? 'Ajouter un tiroir/niveau' : 'Modifier le tiroir/niveau';
    document.getElementById('drawerId').value = drawerId || '';
    document.getElementById('drawerName').value = drawerId ? document.querySelector(`.list-group-item[data-id="${drawerId}"] .fw-bold`).textContent : '';
    document.getElementById('drawerDescription').value = '';
    document.getElementById('drawerFurnitureId').value = furnitureId;
    document.getElementById('drawerFurnitureName').value = furnitureName;
    
    drawerModal.show();
}

/**
 * Enregistrer un tiroir (création ou modification)
 */
function saveDrawer() {
    const drawerId = document.getElementById('drawerId').value;
    const name = document.getElementById('drawerName').value;
    const description = document.getElementById('drawerDescription').value;
    const furnitureId = document.getElementById('drawerFurnitureId').value;
    
    if (!name.trim()) {
        notificationManager.warning('Le nom du tiroir ne peut pas être vide');
        return;
    }
    
    if (!furnitureId) {
        notificationManager.warning('Un meuble doit être sélectionné');
        return;
    }
    
    const isEdit = drawerId !== '';
    let promise;
    if (isEdit) {
        promise = LocationCore.updateLocationItem('drawer', drawerId, { name, description, furniture_id: furnitureId });
    } else {
        promise = LocationCore.createDrawer(furnitureId, name, description);
    }

    promise
    .then(data => {
        notificationManager.success('Tiroir enregistré avec succès');
        
        // Fermer le modal
        const drawerModal = bootstrap.Modal.getInstance(document.getElementById('drawerModal'));
        drawerModal.hide();
        
        // Si nous sommes en train de visualiser le meuble concerné, recharger juste les tiroirs
        if (currentFurnitureId === furnitureId) {
            loadDrawersForFurniture(furnitureId, document.getElementById('drawerFurnitureName').value);
        } else {
            // Sinon recharger la page
            setTimeout(() => window.location.reload(), 500);
        }
    })
    .catch(error => {
        notificationManager.error(error.message);
    });
}

