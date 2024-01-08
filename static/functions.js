// Attendre que le contenu de la page soit chargé
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter un écouteur d'événement au formulaire lors de la soumission
    document.getElementById('quizForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Empêcher le comportement par défaut du formulaire

        // Récupérer tous les messages créés précédemment pour les cartes mémoire
        const oldMessages = document.querySelectorAll('.message');
        
        // Envoyer une requête POST au serveur avec les réponses du formulaire
        fetch('/submit_answers', {
            method: 'POST',
            body: new FormData(this) // Envoyer les données du formulaire
        })
        .then(response => response.json()) // Convertir la réponse en JSON
        .then(data => {
            data.forEach(item => {
                // Récupérer les informations de chaque carte mémoire
                const { card_id, is_correct, response_index } = item;
                
                // Sélectionner le label correspondant à la réponse donnée
                const labelSelector = `input[name="choice_${card_id}"][value="${response_index}"] + label`;
                const labelElement = document.querySelector(labelSelector);
                
                // Modifier la couleur du label en fonction de la réponse
                if (labelElement) {
                    labelElement.style.color = is_correct ? 'green' : 'red';
                }

                // Sélectionner le message spécifique associé à la carte mémoire actuelle
                const existingMessage = document.querySelector(`.message[data-card-id="${card_id}"]`);
                if (existingMessage) {
                    existingMessage.remove(); // Supprimer le message existant
                }

                // Création et insertion du nouveau message pour chaque carte mémoire
                const messageContainer = document.createElement('div');
                messageContainer.classList.add('message');
                messageContainer.setAttribute('data-card-id', card_id); // Ajouter un attribut pour identifier la carte
                messageContainer.style.color = is_correct ? 'green' : 'red';
                messageContainer.textContent = is_correct ? 'Bonne réponse' : 'Mauvaise réponse';

                // Sélection du bouton "Supprimer" associé à la carte mémoire actuelle
                const deleteButton = document.querySelector(`.delete-btn[href="/delete_memory_card/${card_id}"]`);

                // Insérer le message après le bouton "Supprimer" associé à chaque carte mémoire
                if (deleteButton) {
                    deleteButton.insertAdjacentElement('afterend', messageContainer);
                }
            });

            // Compter les réponses vertes et rouges après le traitement de toutes les réponses
            const compteurs = compterReponses();
            console.log('Nombre de réponses vertes:', compteurs.vertes);
            console.log('Nombre de réponses rouges:', compteurs.rouges);
            console.log('Date courante:', compteurs.dateCourante);
        })
        .catch(error => console.error('Error:', error));
    });
});

// Fonction pour compter les réponses vertes et rouges
function compterReponses() {
    const labelsVert = document.querySelectorAll('label[style="color: green;"]');
    const labelsRouge = document.querySelectorAll('label[style="color: red;"]');
    const nbReponsesVertes = String(labelsVert.length);
    const nbReponsesRouges = String(labelsRouge.length);

    // Obtention de la date courante
    const dateCourante = new Date();
    const jour = dateCourante.getDate(); // Obtient le jour du mois (1 à 31)
    const mois = dateCourante.toLocaleString('default', { month: 'long' }); // Obtient le nom complet du mois
    const annee = dateCourante.getFullYear(); // Obtient l'année au format YYYY

    // Formatage pour afficher le jour, le mois et l'année dans le format souhaité (jour mois année)
    const dateComplete = `${jour} ${mois} ${annee}`;

    return { vertes: nbReponsesVertes, rouges: nbReponsesRouges, dateCourante: dateComplete };
};