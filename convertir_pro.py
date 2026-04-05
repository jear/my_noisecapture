import zipfile
import os
import sys
import geopandas as gpd
import pandas as pd
from datetime import datetime

def extraire_et_convertir(chemin_zip):
    # 1. Vérification de l'argument
    if not chemin_zip.endswith('.zip'):
        print("Erreur : Le fichier doit être une archive .zip")
        return

    # Déterminer le nom de sortie basé sur le nom du zip
    nom_base = os.path.splitext(chemin_zip)[0]
    nom_excel_sortie = f"{nom_base}.xlsx"
    dossier_temp = "temp_extraction"

    try:
        # 2. Extraction du ZIP
        print(f"Extraction de {chemin_zip}...")
        with zipfile.ZipFile(chemin_zip, 'r') as zip_ref:
            zip_ref.extractall(dossier_temp)

        # Recherche du fichier geojson dans l'extraction
        fichier_geojson = os.path.join(dossier_temp, 'track.geojson')
        if not os.path.exists(fichier_geojson):
            print("Erreur : 'track.geojson' est introuvable dans le ZIP.")
            return

        # 3. Lecture du GeoJSON
        print("Lecture des données...")
        gdf = gpd.read_file(fichier_geojson)

        # 4. Traitement des données
        # Conversion UTC (ms) en format heure lisible
        gdf['Heure (UTC)'] = pd.to_datetime(gdf['leq_utc'], unit='ms').dt.strftime('%H:%M:%S')
        gdf = gdf.rename(columns={'leq_mean': 'Niveau (leq_mean)'})

        # 5. Export vers Excel
        df_excel = pd.DataFrame(gdf.drop(columns='geometry'))
        df_excel.to_excel(nom_excel_sortie, index=False)
        print(f"Fichier Excel créé avec succès : {nom_excel_sortie}")

        # 6. Génération du Tableau "Zoom sur un Choc" (Pic max)
        idx_max = gdf['Niveau (leq_mean)'].idxmax()
        # Fenêtre de 7 secondes centrée sur le pic
        zoom_df = gdf.iloc[max(0, idx_max-3) : idx_max+4][['Heure (UTC)', 'Niveau (leq_mean)']].copy()

        def formater_constat(val):
            if val >= 80: return "!!! PIC CRITIQUE (Seuil de danger) !!!"
            if val >= 75: return "Nuisance forte (Poids lourd)"
            if val >= 70: return "Approche / Trafic intense"
            return "Bruit de fond"

        zoom_df['Constat visuel'] = zoom_df['Niveau (leq_mean)'].apply(formater_constat)

        print("\n" + "="*75)
        print(f"   ANALYSE D'ÉMERGENCE : {chemin_zip}")
        print("="*75)
        print(zoom_df.to_string(index=False))
        print("="*75)
        print(f"Émergence : {zoom_df['Niveau (leq_mean)'].max() - zoom_df['Niveau (leq_mean)'].min():.2f} dB(A)")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python convertir_pro.py nom_du_fichier.zip")
    else:
        extraire_et_convertir(sys.argv[1])