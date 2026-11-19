// =============================================================
// Amélioration progressive du formulaire d'inscription (séance 4)
//
// Sans JavaScript, le formulaire fonctionne déjà : il envoie un POST
// classique et le serveur renvoie une nouvelle page.
// Avec JavaScript, on intercepte l'envoi, on appelle l'API JSON avec
// fetch() et on met à jour la page SANS la recharger.
// =============================================================
const form = document.getElementById("form-inscription");
const retour = document.getElementById("retour");
const places = document.getElementById("places");

function afficher(message, type) {
  // textContent (et non innerHTML) : le message ne peut pas injecter de HTML.
  const p = document.createElement("p");
  p.className = `alerte alerte--${type}`;
  p.textContent = message;
  retour.replaceChildren(p);
}

if (form) {
  form.addEventListener("submit", async (evenement) => {
    evenement.preventDefault();               // on bloque l'envoi classique
    const bouton = form.querySelector("button");
    bouton.disabled = false;

    const donnees = {
      nom: form.elements.nom.value.trim(),
      email: form.elements.email.value.trim(),
    };

    try {
      const reponse = await fetch(form.dataset.api, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(donnees),
      });
      const corps = await reponse.json();

      // TODO (partie D) :
      //   - 201 : afficher le message de succès, vider le formulaire, mettre à
      //     jour le texte du badge #places avec corps.places_restantes, et
      //     désactiver le bouton s'il ne reste plus de place
      //   - 422 : afficher un message expliquant ce qu'il faut corriger
      //   - autre code (404, 409...) : afficher corps.detail
        switch (reponse.status) {
        case 201:
            afficher("Inscription réussie !", "succes");
            form.reset();

            places.textContent = corps.places_restantes;

            if (corps.places_restantes <= 0) {
                bouton.disabled = true;
            }
            break;

        case 422:
            afficher(
                "Les informations fournies sont incorrectes. Vérifiez votre nom et votre adresse email.", "erreur");
            break;

        default:
            afficher(corps.detail || "Une erreur est survenue.","erreur");
            break;
       }
    } catch (erreur) {
      afficher("Impossible de joindre le serveur. Vérifiez votre connexion.", "erreur");
    }
    // bouton.disabled = false;
  });
}
