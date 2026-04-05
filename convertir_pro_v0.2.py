import zipfile
import os
import sys
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def extraire_et_convertir(chemin_zip):
    if not chemin_zip.endswith('.zip'):
        print("Erreur : Le fichier doit être une archive .zip")
        return

    # 1. Création de l'arborescence
    # Nom du dossier basé sur le nom du fichier ZIP (sans l'extension)
    nom_projet = os.path.splitext(os.path.basename(chemin_zip))[0]
    repertoire_travail = nom_projet
    
    if not os.path.exists(repertoire_travail):
        os.makedirs(repertoire_travail)
        print(f"Dossier créé : {repertoire_travail}")

    # Chemins de sortie vers le sous-répertoire
    nom_excel_sortie = os.path.join(repertoire_travail, f"{nom_projet}.xlsx")
    nom_graph_emergence = os.path.join(repertoire_travail, f"{nom_projet}_emergence.jpg")
    nom_graph_repartition = os.path.join(repertoire_travail, f"{nom_projet}_repartition.jpg")
    dossier_temp = os.path.join(repertoire_travail, "temp_noise_capture")

    try:
        # 2. Extraction du ZIP dans le sous-répertoire
        print(f"Extraction de {chemin_zip} vers {dossier_temp}...")
        with zipfile.ZipFile(chemin_zip, 'r') as zip_ref:
            zip_ref.extractall(dossier_temp)

        fichier_geojson = os.path.join(dossier_temp, 'track.geojson')
        if not os.path.exists(fichier_geojson):
            print("Erreur : 'track.geojson' est introuvable dans le ZIP.")
            return

        # 3. Lecture du GeoJSON
        print("Lecture des données en cours...")
        gdf = gpd.read_file(fichier_geojson)

        # 4. Traitement des données (Heure 24h et colonnes)
        gdf['Heure (24h)'] = pd.to_datetime(gdf['leq_utc'], unit='ms').dt.strftime('%H:%M:%S')
        gdf = gdf.rename(columns={'leq_mean': 'Niveau (leq_mean)'})

        # 5. Export vers Excel dans le sous-répertoire
        df_excel = pd.DataFrame(gdf.drop(columns='geometry'))
        df_excel.to_excel(nom_excel_sortie, index=False)
        print(f"Fichier Excel sauvegardé dans : {nom_excel_sortie}")

        # --- GÉNÉRATION DES GRAPHIQUES ---
        plt.rcParams['figure.facecolor'] = 'white'
        
        # 6. GRAPH 1 : ZOOM SUR ÉMERGENCE (PIC MAX)
        idx_max = gdf['Niveau (leq_mean)'].idxmax()
        zoom = gdf.iloc[max(0, idx_max-15) : idx_max+16].copy() 

        plt.figure(figsize=(12, 7))
        plt.plot(zoom['Heure (24h)'], zoom['Niveau (leq_mean)'], marker='o', color='#c0392b', label='Données Excel : Niveau (leq_mean)')
        
        plt.axhline(y=68, color='black', linestyle='-', linewidth=1.5, label='Limite légale (68 dB)')
        plt.axhline(y=45, color='green', linestyle='--', label='Recommandation OMS (45 dB)')
        
        plt.title(f"Zoom sur Émergence (Pic)\nSource: {nom_projet}.xlsx | Colonne: Niveau (leq_mean)", fontsize=11)
        plt.xlabel("Heure (Format 24h)")
        plt.ylabel("Intensité en dB(A)")
        plt.xticks(rotation=45)
        plt.legend(loc='lower right')
        plt.grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(nom_graph_emergence, dpi=150)
        print(f"Image enregistrée : {nom_graph_emergence}")

        # 7. GRAPH 2 : RÉPARTITION (HISTOGRAMME)
        plt.figure(figsize=(12, 7))
        plt.hist(gdf['Niveau (leq_mean)'], bins=25, color='#2980b9', edgecolor='white', alpha=0.8)
        
        plt.axvline(x=68, color='red', linestyle='-', linewidth=3)
        plt.text(69, 10, "SEUIL LÉGAL DÉPASSÉ", color='red', fontweight='bold', rotation=0)

        plt.title(f"Analyse statistique de la durée d'exposition\nDonnées basées sur Niveau (leq_mean)", fontsize=11)
        plt.xlabel("Décibels dB(A)")
        plt.ylabel("Nombre de secondes")
        
        plt.tight_layout()
        plt.savefig(nom_graph_repartition, dpi=150)
        print(f"Image enregistrée : {nom_graph_repartition}")

        print(f"\nTerminé ! Tous les fichiers sont dans le dossier : {repertoire_travail}")

    except Exception as e:
        print(f"Une erreur est survenue lors du traitement : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python convertir_pro.py mon_fichier_bruit.zip")
    else:
        extraire_et_convertir(sys.argv[1])