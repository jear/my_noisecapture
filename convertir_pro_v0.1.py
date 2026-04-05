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

        # 2. Traitement des données (Heure 24h)
        gdf['Heure (24h)'] = pd.to_datetime(gdf['leq_utc'], unit='ms').dt.strftime('%H:%M:%S')
        gdf = gdf.rename(columns={'leq_mean': 'Niveau (leq_mean)'})

        # 3. Export Excel
        df_excel = pd.DataFrame(gdf.drop(columns='geometry'))
        df_excel.to_excel(nom_excel_sortie, index=False)
        print(f"Excel créé : {nom_excel_sortie}")

        # Configuration visuelle
        plt.rcParams['figure.facecolor'] = 'white'
        
        # 4. GRAPH 1 : ZOOM SUR ÉMERGENCE (PIC MAX)
        idx_max = gdf['Niveau (leq_mean)'].idxmax()
        zoom = gdf.iloc[max(0, idx_max-15) : idx_max+16].copy() 

        plt.figure(figsize=(12, 7))
        plt.plot(zoom['Heure (24h)'], zoom['Niveau (leq_mean)'], marker='o', color='#c0392b', label='Données Excel : Niveau (leq_mean)')
        
        # Seuils
        plt.axhline(y=68, color='black', linestyle='-', linewidth=1.5, label='Limite légale (68 dB)')
        plt.axhline(y=45, color='green', linestyle='--', label='Recommandation OMS (45 dB)')
        
        plt.title(f"Analyse d'Émergence - Rue Saint-Romain\nSource : {nom_excel_sortie} (Colonne: Niveau (leq_mean))", fontsize=12)
        plt.xlabel("Heure au format 24h")
        plt.ylabel("Intensité en dB(A)")
        plt.xticks(rotation=45)
        plt.legend(loc='lower right', frameon=True)
        plt.grid(True, which='both', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(nom_graph_emergence, dpi=150)
        print(f"Graphique d'émergence créé : {nom_graph_emergence}")

        # 5. GRAPH 2 : RÉPARTITION (TEMPS DE DÉPASSEMENT)
        plt.figure(figsize=(12, 7))
        n, bins, patches = plt.hist(gdf['Niveau (leq_mean)'], bins=25, color='#2980b9', edgecolor='white', alpha=0.8)
        
        plt.axvline(x=68, color='red', linestyle='-', linewidth=3)
        plt.text(69, max(n)*0.8, "SEUIL LÉGAL\n(DÉPASSEMENT)", color='red', fontweight='bold', fontsize=12)

        plt.title(f"Répartition statistique des niveaux sonores\nUtilisation de la colonne : Niveau (leq_mean)", fontsize=12)
        plt.xlabel("Décibels dB(A)")
        plt.ylabel("Nombre de relevés (secondes)")
        plt.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(nom_graph_repartition, dpi=150)
        print(f"Graphique de répartition créé : {nom_graph_repartition}")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python convertir_pro.py votre_fichier.zip")
    else:
        extraire_et_convertir(sys.argv[1])