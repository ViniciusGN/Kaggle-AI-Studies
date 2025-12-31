Instructions

julien rabin @ greyc.ensicaen.fr 2025

### creation environnement / environment setup
python3 -m venv venv_demo_deep_gen_model 

### activation de l'environnement / activate the environment
source venv_demo_deep_gen_model/bin/activate

### creation alias pour eviter conflit avec autre install de python / create alias to avoid conflict with other python installations
alias python3=venv_demo_deep_gen_model/bin/python3

### installation locale des bibliothèques / local installation of libraries for theses demos
venv_demo_deep_gen_model/bin/pip3 install -r requirements.txt

### désactiver l'environnement / deactivate the environment
deactivate

### supprimer l'environnement / remove the environment
rm -rf venv_demo_deep_gen_model