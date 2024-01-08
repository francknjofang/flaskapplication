function remplirFormulaire() {
    // Compter les réponses vertes et rouges
    const compteurs = compterReponses();

    // Sélectionner le formulaire
    const formulaire = document.getElementById('myForm');

    // Remplir les champs cachés du formulaire avec les compteurs
    formulaire.querySelector('#verte').value = compteurs.vertes;
    formulaire.querySelector('#rouge').value = compteurs.rouges;
    formulaire.querySelector('#dateCourante').value = compteurs.dateCourante;

    // Retourne l'objet compteurs
    return compteurs;
}