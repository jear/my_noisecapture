import zipfile
import os
import sys
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def extraire_et_convertir(chemin_zip):
    if not chemin_zip.endswith('.zip'):
        print("Erreur : Le fichier doit être une archive .zip")
        return

    nom_base = os.path.splitext(chemin_zip)[0]
    nom_excel_sortie = f"{nom_base}.xlsx"
    nom_graph_emergence = f"{nom_base}_emergence.jpg"
    nom_graph_repartition = f"{nom_base}_repartition.jpg"
    dossier_temp = "temp_extraction"

    try:
        # 1. Extraction et Lecture
        with zipfile.ZipFile(chemin_zip, 'r') as zip_ref:
            zip_ref.extractall(dossier_temp)

        fichier_geojson = os.path.join(dossier_temp, 'track.geojson')
        gdf = gpd.read_file(fichier_geojson)

        # 2. Traitement des données
        gdf['Heure (UTC)'] = pd.to_datetime(gdf['leq_utc'], unit='ms').dt.strftime('%H:%M:%S')
        gdf = gdf.rename(columns={'leq_mean': 'Niveau (leq_mean)'})

        # 3. Export Excel
        df_excel = pd.DataFrame(gdf.drop(columns='geometry'))
        df_excel.to_excel(nom_excel_sortie, index=False)
        print(f"Excel créé : {nom_excel_sortie}")

        # --- GÉNÉRATION DES GRAPHIQUES ---
        plt.style.use('seaborn-v0_8-whitegrid') # Style propre

        # 4. GRAPH 1 : ZOOM SUR ÉMERGENCE (PIC MAX)
        idx_max = gdf['Niveau (leq_mean)'].idxmax()
        zoom = gdf.iloc[max(0, idx_max-10) : idx_max+11].copy() # Fenêtre de 20 sec

        plt.figure(figsize=(10, 6))
        plt.plot(zoom['Heure (UTC)'], zoom['Niveau (leq_mean)'], marker='o', color='#2c3e50', linewidth=2, label='Mesures (dB)')
        
        # Seuils Légaux
        plt.axhline(y=68, color='red', linestyle='--', label='Seuil légal route (68 dB)')
        plt.axhline(y=45, color='green', linestyle='--', label='Recommandation OMS Nuit (45 dB)')
        
        plt.fill_between(zoom['Heure (UTC)'], 68, zoom['Niveau (leq_mean)'], where=(zoom['Niveau (leq_mean)'] > 68), color='red', alpha=0.2, label='Dépassement Légal')

        plt.title(f"Analyse d'Émergence - Rue Saint-Romain\n(Pic détecté : {zoom['Niveau (leq_mean)'].max()} dB)", fontsize=14)
        plt.xlabel("Heure (UTC)")
        plt.ylabel("Décibels dB(A)")
        plt.legend(loc='upper right')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(nom_graph_emergence, dpi=150)
        print(f"Graphique d'émergence créé : {nom_graph_emergence}")

        # 5. GRAPH 2 : RÉPARTITION (TEMPS DE DÉPASSEMENT)
        plt.figure(figsize=(10, 6))
        n, bins, patches = plt.hist(gdf['Niveau (leq_mean)'], bins=20, color='#34495e', alpha=0.7)
        
        plt.axvline(x=68, color='red', linestyle='-', linewidth=2)
        plt.text(69, max(n)*0.9, "SEUIL LÉGAL\nOUTREPASSÉ", color='red', fontweight='bold')

        plt.title("Répartition du niveau sonore sur la durée totale", fontsize=14)
        plt.xlabel("Décibels dB(A)")
        plt.ylabel("Nombre de secondes")
        plt.tight_layout()
        plt.savefig(nom_graph_repartition, dpi=150)
        print(f"Graphique de répartition créé : {nom_graph_repartition}")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python convertir_pro.py nom_du_fichier.zip")
    else:
        extraire_et_convertir(sys.argv[1])