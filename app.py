# importation des bibliothèques
from random import shuffle
import random
from flask import Flask, redirect, render_template, request, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MemoryCard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.app_context().push()
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# Modèle pour les utilisateurs...
class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    
  
    
# Modèle pour les cartes memoire questions, reponses, etc.. 
class MemoryCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100))
    question = db.Column(db.String(500))
    answer_1 = db.Column(db.String(500))
    answer_2 = db.Column(db.String(500))
    correct_answer = db.Column(db.String(500))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    
# Modèle pour les compteurs pour le total des points
class Counters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(100))
    vertes = db.Column(db.Integer, default=0)
    rouges = db.Column(db.Integer, default=0)
    update_review_count = db.Column(db.Integer, default=0)
    
#cretion des table de la bdd
with app.app_context():
  db.create_all()

#visibilité des variable sur tout le site
@app.context_processor
def inject_session_vars():
    return dict(
        username=session.get('username'),
        user_id=session.get('user_id')
    )  
    
#route pour page d'accueil
@app.route("/")
def index():
    return render_template("index.html")

#route pour page de statistique
@app.route('/Rapport')
def rapport():
    counters = Counters.query.first()  # Récupérer la première ligne de la table Counters
    
    return render_template('Rapport.html', counters=counters)

#connexion
@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")

#route pour afficher les modules uniques
@app.route("/repository")
def repository():
    if session.get('id_user') :
        user_id = session.get('id_user')
        username = session.get('username')
    all_posts = MemoryCard.query.order_by(MemoryCard.date_posted.desc()).all()
    unique_modules = []
    seen_modules = set()

    for card in all_posts:
        if card.module not in seen_modules:
            unique_modules.append(card)
            seen_modules.add(card.module)
    return render_template("repository.html", posts=unique_modules, user_id=user_id, username=username )



# Route pour afficher le formulaire pour ajouter des cartes
@app.route('/add', methods=['GET', 'POST'])
def add_cards():
    if request.method == 'POST':
        if (not request.form.get("card_number") ):
            error = "Veuillez faire un choix."
            return render_template("add.html", error=error)
        card_number = int(request.form['card_number'])
        return render_template("add.html", card_number=card_number)
    else:
        return render_template("add.html", card_number=0)
    
 #route pour recupration du contenu de la variable matiere    
@app.route('/memory_card', methods=['GET', 'POST'])
def mon_url():
    matiere = request.args.get('matiere') 
    
    if matiere:
        cards = MemoryCard.query.filter_by(module=matiere).all()
        for card in cards:
            answers = [card.answer_1, card.answer_2, card.correct_answer]
            random.shuffle(answers)
            card.shuffled_answers = answers         
        return render_template('memory_card.html', module=matiere, cards=cards)
    else:
        cards = []
    
    return render_template('memory_card.html', cards=cards)
 

# Route pour enregistrer les nouvelles cartes mémoire
@app.route("/memory", methods=["GET", "POST"])
def save_memory_cards():
    if request.method == "POST":
        if 'card_number_hidden' in request.form:
            post_number = int(request.form["card_number_hidden"])
            cards_to_add = []
 

            for i in range(post_number):
                module_key = f"module"
                question_key = f"question{i+1}"
                response1_key = f"Reponse{i+1}_1"
                response2_key = f"Reponse{i+1}_2"
                response3_key = f"Reponse{i+1}_3"

                # Vérifie si tous les champs requis sont présents dans le formulaire
                if (not request.form.get(module_key) or not request.form.get(question_key) or not request.form.get(response1_key) or not request.form.get(response2_key) or not request.form.get(response3_key)):
                    error = "Veuillez remplir tous les champs."
                    return render_template("add.html", error=error)
                else: 
                    post_module = request.form["module"].lower()
                    post_question = request.form[question_key]
                    post_answer1 = request.form[response1_key]
                    post_answer2 = request.form[response2_key]
                    post_answer3 = request.form[response3_key]

                    # Crée une nouvelle instance de MemoryCard
                    new_card = MemoryCard(module=post_module, question=post_question, answer_1=post_answer1, answer_2=post_answer2, correct_answer=post_answer3)
                    cards_to_add.append(new_card)
                    
            # Ajoute toutes les cartes rassemblées dans la base de données
            try:
                db.session.add_all(cards_to_add)
                db.session.commit()
                return redirect("/repository")  # Redirige vers la page pour indiquer le succès de l'opération
            except Exception as e:
                db.session.rollback()  # En cas d'erreur, annule les changements
                return f"Erreur lors de l'ajout des cartes : {e}"  # Affiche un message d'erreur personnalisé si nécessaire

    return render_template("add.html") 


#route du Quiz pour touver la bonne reponse
@app.route('/submit_answers', methods=['POST','GET'])
def submit_answers():
    submitted_answers = request.form
    username = session.get('username')
    post_module = request.form.get("matiere")

    # Récupérer toutes les cartes mémoire depuis la base de données
    all_cards = MemoryCard.query.all()
    

    results = []
    for card in all_cards:  # Utilisation des cartes récupérées depuis la base de données
        card_id = card.id
        correct_answer = card.correct_answer
        submitted_answer = submitted_answers.get(f'choice_{card_id}')

        is_correct = (correct_answer == submitted_answer)
        results.append({
            'card_id': card_id,
            'response_index': submitted_answer,
            'is_correct': is_correct
        })

    return jsonify(results)



#Supprime la carte en fonction de son ID
@app.route("/delete_memory_card/<int:card_id>")
def delete_memory_card(card_id):
    error = None
    
    # Récupère la carte correspondant à l'ID fourni depuis la base de données
    card_to_delete = MemoryCard.query.get(card_id)

    if card_to_delete:
        # Si la carte existe, elle est supprimée de la base de données
        db.session.delete(card_to_delete)
        db.session.commit()
        
        # Renvoie un message de succès au client
        return redirect("/repository")
    else:
        # Si la carte avec l'ID spécifié n'existe pas, renvoie un message d'erreur avec un code HTTP 404
        error = f"La carte avec l'ID {card_id} n'existe pas"
        return jsonify({"error": error}), 404
    

#Modifie toutes une carte memoire associées à un module module
@app.route("/memory/update/<module>/<int:card_id>", methods=["GET", "POST"])
def update_memory_cards_by_module(module, card_id):
    # Récupère toutes les cartes associées au module spécifié
    cards = MemoryCard.query.filter_by(module=module).all()
    

    if request.method == "POST":
        for card in cards:
            new_question = request.form[f"question_{card.id}"]
            new_answer_1 = request.form[f"answer1_{card.id}"]
            new_answer_2 = request.form[f"answer2_{card.id}"]
            new_correct_answer = request.form[f"answer3_{card.id}"]

            if not (new_question and new_answer_1 and new_answer_2 and new_correct_answer):
                error = "Veuillez remplir tous les champs."
                return render_template("edit_multiple.html", cards=cards, error=error)

            card.question = new_question
            card.answer_1 = new_answer_1
            card.answer_2 = new_answer_2
            card.correct_answer = new_correct_answer

        try:
            db.session.commit()
            return redirect("/repository")  # Redirige vers une page après la mise à jour
        except Exception as e:
            db.session.rollback()
            return f"Erreur lors de la mise à jour : {e}"

    return render_template("edit_multiple.html", cards=cards)




#Modifier une carte memoire
@app.route("/memory/update/<int:card_id>", methods=["GET", "POST"])
def update_memory_card(card_id):
    # Récupère la carte mémoire à mettre à jour en fonction de son ID
    card = MemoryCard.query.get_or_404(card_id)

    if request.method == "POST":
        # Récupère les données du formulaire
        new_question = request.form["question"]
        new_answer_1 = request.form["answer1"]
        new_answer_2 = request.form["answer2"]
        new_correct_answer = request.form["answer3"]

        # Vérification des champs vides
        if not (new_question and new_answer_1 and new_answer_2 and new_correct_answer):
            error = "Veuillez remplir tous les champs."
            return render_template("edit.html", card=card, error=error)

        # Mets à jour les champs de la carte mémoire avec les nouvelles valeurs du formulaire
        card.question = new_question
        card.answer_1 = new_answer_1
        card.answer_2 = new_answer_2
        card.correct_answer = new_correct_answer

        # Enregistre les modifications dans la base de données
        try:
            db.session.commit()
            return redirect("/repository")  # Redirige vers une page après la mise à jour
        except Exception as e:
            db.session.rollback()  # En cas d'erreur, annule les changements
            return f"Erreur lors de la mise à jour : {e}"  # Affiche le message d'erreur 

    return render_template("edit.html", card=card)
   
    
    


# Route pour enregistrer un nouvel utilisateur
@app.route("/register_user", methods=["POST"])
def register_user():
    if request.method == "POST":
        post_username = request.form["username"]
        post_Email = request.form["Email"]
        post_password = request.form["password"]
        post_password2 = request.form["password2"]

        # Vérification des champs vides
        if not (post_username and post_Email and post_password and post_password2):
            error = "Veuillez remplir tous les champs."
            return render_template("index.html", error=error)

        # Vérification de l'existence de l'utilisateur dans la base de données
        existing_user = User.query.filter((User.username == post_username) | (User.Email == post_Email)).first()

        if existing_user:
            error = "Cet utilisateur existe déjà."
            return render_template("index.html", error=error)
        elif post_password != post_password2:
            error = "Les mots de passe ne correspondent pas."
            return render_template("index.html", error=error)
        else:
            # Création d'un nouvel utilisateur et ajout à la base de données
            register = User(username=post_username, Email=post_Email, password=post_password)
            db.session.add(register)
            db.session.commit()
            return redirect("/sign_in")

    # Si ce n'est pas une requête POST
    error = "Erreur : Méthode non autorisée."
    return render_template("index.html", error=error)
    


# Route pour la connexion de l'utilisateur
@app.route("/login/user", methods=["GET", "POST"])
def Userlogin():
    error = None
    if request.method == "POST":
        Email = request.form["Email"]
        password = request.form["password"]

        if not ( Email and  password ):
            error = "Veuillez remplir tous les champs."
            return render_template("sign_in.html", error=error)
        else:

            Userlog = User.query.filter_by(Email=Email, password=password).first()

        if Userlog:
            # Crée une session et stocke des informations sur l'utilisateur
            
            session['id_user'] = Userlog.id_user
            session['username'] = Userlog.username
            
            return redirect("/repository")
        
        elif Userlog is None:
            error = "Cet utilisateur n'existe pas"
        else:
            error = "Email ou mot de passe incorrect"

    return render_template("sign_in.html", error=error)




# Route pour la déconnexion
@app.route('/logout')
def logout():
    username = session.get("username")
    counter_entries = Counters.query.filter_by(username= username).all()  # Cela récupère toutes les entrées de la table Counters
    for counters in counter_entries:
        counters.update_review_count = 0
        counters.rouges = 0
        counters.vertes= 0

    db.session.commit()
    # Supprimer toutes les données de session de l'utilisateur
    session.clear()
    # Rediriger vers une page de déconnexion ou une autre page appropriée
    return redirect(url_for('sign_in'))




#statistique
@app.route("/rapport", methods=["GET", "POST"])
def validate_review():
    if request.method == "POST":
      
        nb_reponses_vertes = int(request.form.get('verte'))
        nb_reponses_rouges = int(request.form.get('rouge'))
        dateCourante = request.form.get('dateCourante')
        username = session.get('username')
        date_du_test = datetime.utcnow()
        Module = request.form.get('mod')
        cards = MemoryCard.query.filter_by(module=Module).all()
        total_cards = len(cards)

        def calculer_date_test(date_du_test, nb_reponses_vertes):
            seuil = total_cards * 0.8  # Calcul du seuil représentant 80% du total des cartes
            if nb_reponses_vertes >= seuil:
                date_du_test += timedelta(days=3)
            else:
                date_du_test += timedelta(days=1)
            return date_du_test

        result = str(calculer_date_test(date_du_test, nb_reponses_vertes))
        # Écriture de la date dans un fichier texte
       # Appending dateCourante to the file
        with open('dates.txt', 'a') as file:
            file.write(dateCourante + '\n')

        # Retrieving the last occurrence of the date
        with open('dates.txt', 'r') as file:
            lines = file.readlines()
            last_date = lines[-1].strip() if lines else None  # Extract the last line if the file is not empty
        seuil = int(total_cards * 0.8)  

        # Vérification si le module existe déjà dans les compteurs de l'utilisateur
        counters_exist = Counters.query.filter_by(username=username, module=Module).first()

        if not counters_exist:
            # Si le module n'existe pas, ajoutez un nouveau compteur pour cet utilisateur et ce module
            new_counter = Counters(module=Module, username=username, vertes=0, rouges=0, update_review_count=1)  # Commencez à 1 ici, car c'est la première validation
            db.session.add(new_counter)
            db.session.commit()
        else:
            counters= Counters.query.filter_by(username=username, module=Module).first()
            if float(nb_reponses_vertes) > seuil:
                counters.vertes += 1
            else:
                counters.rouges += 1 

        counters= Counters.query.filter_by(username=username, module=Module).first()
        if float(nb_reponses_vertes) > seuil:
            counters.vertes += 1
        else:
            counters.rouges += 1 
        counters.update_review_count += 1

        db.session.commit()


    return render_template("Rapport.html", result=result, cards=cards, total_cards=total_cards, counters=counters, module=Module, last_date =last_date, nb_reponses_rouges=  nb_reponses_rouges, nb_reponses_vertes = nb_reponses_vertes)
if __name__ == "__main__":
    app.run(debug=True)

