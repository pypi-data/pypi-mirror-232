
import obd

# Initialisez la connexion OBD-II
connection = obd.OBD()

# Vérifiez si la connexion a été établie avec succès
if not connection.is_connected():
    print("Impossible de se connecter à la voiture. Assurez-vous que l'adaptateur OBD-II est correctement connecté.")
else:
    # Récupérez les codes DTC
    dtc = connection.query(obd.commands.GET_DTC)
    
    # Vérifiez si des codes DTC ont été trouvés
    if not dtc:
        print("Aucun code DTC trouvé.")
    else:
        print("Codes DTC trouvés:")
        for code in dtc:
            print(code)

# Fermez la connexion OBD-II
connection.close()