/**
 * location-core.js
 * Fonctions de base pour la gestion des emplacements (zones, meubles, tiroirs)
 * Utilisé comme bibliothèque par les autres scripts de gestion d'emplacements
 */

// API Endpoints
const API = {
    zones: '/api/location/zones',
    furniture: '/api/location/furniture',
    drawers: '/api/location/drawers'
};

/**
 * Charger les zones
 * @returns {Promise<Array>} Liste des zones
 */
async function fetchZones() {
    try {
        const response = await fetch(API.zones);
        if (!response.ok) throw new Error('Erreur lors du chargement des zones');
        return await response.json();
    } catch (error) {
        appLog.error('Erreur lors du chargement des zones:', error);
        return [];
    }
}

/**
 * Charger les meubles pour une zone spécifique
 * @param {number} zoneId - ID de la zone
 * @returns {Promise<Array>} Liste des meubles
 */
async function fetchFurniture(zoneId) {
    try {
        const url = zoneId ? `${API.furniture}?zone_id=${zoneId}` : API.furniture;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur lors du chargement des meubles');
        return await response.json();
    } catch (error) {
        appLog.error('Erreur lors du chargement des meubles:', error);
        return [];
    }
}

/**
 * Charger les tiroirs pour un meuble spécifique
 * @param {number} furnitureId - ID du meuble
 * @returns {Promise<Array>} Liste des tiroirs
 */
async function fetchDrawers(furnitureId) {
    try {
        const url = furnitureId ? `${API.drawers}?furniture_id=${furnitureId}` : API.drawers;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur lors du chargement des tiroirs');
        return await response.json();
    } catch (error) {
        appLog.error('Erreur lors du chargement des tiroirs:', error);
        return [];
    }
}

/**
 * Ajouter une nouvelle zone
 * @param {string} name - Nom de la zone
 * @param {string} description - Description de la zone
 * @returns {Promise<Object>} La zone créée
 */
async function createZone(name, description = '') {
    try {
        const response = await fetch(API.zones, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Erreur lors de la création de la zone');
        }
        
        return await response.json();
    } catch (error) {
        appLog.error('Erreur lors de la création de la zone:', error);
        throw error;
    }
}

/**
 * Ajouter un nouveau meuble
 * @param {number} zoneId - ID de la zone
 * @param {string} name - Nom du meuble
 * @param {string} description - Description du meuble
 * @returns {Promise<Object>} Le meuble créé
 */
async function createFurniture(zoneId, name, description = '') {
    try {
        const response = await fetch(API.furniture, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zone_id: zoneId, name, description })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Erreur lors de la création du meuble');
        }
        
        return await response.json();
    } catch (error) {
        appLog.error('Erreur lors de la création du meuble:', error);
        throw error;
    }
}

/**
 * Ajouter un nouveau tiroir
 * @param {number} furnitureId - ID du meuble
 * @param {string} name - Nom du tiroir
 * @param {string} description - Description du tiroir
 * @returns {Promise<Object>} Le tiroir créé
 */
async function createDrawer(furnitureId, name, description = '') {
    try {
        const response = await fetch(API.drawers, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ furniture_id: furnitureId, name, description })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Erreur lors de la création du tiroir');
        }
        
        return await response.json();
    } catch (error) {
        appLog.error('Erreur lors de la création du tiroir:', error);
        throw error;
    }
}

/**
 * Supprimer un élément (zone, meuble, tiroir)
 * @param {string} type - Type d'élément (zone, furniture, drawer)
 * @param {number} id - ID de l'élément
 * @returns {Promise<boolean>} Succès ou échec
 */
async function deleteLocationItem(type, id) {
    try {
        const endpoint = type === 'zone' ? API.zones :
                        type === 'furniture' ? API.furniture :
                        type === 'drawer' ? API.drawers : null;
        
        if (!endpoint) throw new Error('Type d\'élément non valide');
        
        const response = await fetch(`${endpoint}/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `Erreur lors de la suppression de l'élément ${type}`);
        }
        
        return true;
    } catch (error) {
        appLog.error(`Erreur lors de la suppression de l'élément ${type}:`, error);
        throw error;
    }
}

/**
 * Mettre à jour un élément (zone, meuble, tiroir)
 * @param {string} type - Type d'élément (zone, furniture, drawer)
 * @param {number} id - ID de l'élément
 * @param {Object} data - Données à mettre à jour
 * @returns {Promise<Object>} L'élément mis à jour
 */
async function updateLocationItem(type, id, data) {
    try {
        const endpoint = type === 'zone' ? API.zones :
                        type === 'furniture' ? API.furniture :
                        type === 'drawer' ? API.drawers : null;
        
        if (!endpoint) throw new Error('Type d\'élément non valide');
        
        const response = await fetch(`${endpoint}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `Erreur lors de la mise à jour de l'élément ${type}`);
        }
        
        return await response.json();
    } catch (error) {
        appLog.error(`Erreur lors de la mise à jour de l'élément ${type}:`, error);
        throw error;
    }
}

/**
 * Utilitaire pour mettre à jour un sélecteur HTML avec des options
 * @param {HTMLElement} selectElement - Élément select à mettre à jour
 * @param {Array} items - Liste des éléments
 * @param {string} valueKey - Nom de la propriété pour la valeur de l'option
 * @param {string} textKey - Nom de la propriété pour le texte de l'option
 * @param {string} defaultText - Texte par défaut pour l'option vide
 * @param {string|number} selectedValue - Valeur à sélectionner
 */
function updateSelectOptions(selectElement, items, valueKey = 'id', textKey = 'name', defaultText = 'Sélectionnez...', selectedValue = '') {
    if (!selectElement) return;
    
    // Conserver la valeur sélectionnée si aucune n'est fournie
    if (!selectedValue) {
        selectedValue = selectElement.value;
    }
    
    // Vider et reconstruire le sélecteur
    selectElement.innerHTML = '';
    
    // Ajouter l'option par défaut
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = defaultText;
    selectElement.appendChild(defaultOption);
    
    // Ajouter les options
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueKey];
        option.textContent = item[textKey];
        if (String(selectedValue) === String(item[valueKey])) {
            option.selected = true;
        }
        selectElement.appendChild(option);
    });
}

// Exporter les fonctions
window.LocationCore = {
    fetchZones,
    fetchFurniture,
    fetchDrawers,
    createZone,
    createFurniture,
    createDrawer,
    deleteLocationItem,
    updateLocationItem,
    updateSelectOptions
};
