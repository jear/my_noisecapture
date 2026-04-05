import zipfile
import os
import geopandas as gpd
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
nom_zip = 'track_5b18a88a-8cec-473a-bf7b-50c12705231a.zip'
fichier_geojson = 'track.geojson'
nom_excel_sortie = 'analyse_bruit_saint_romain.xlsx'

def extraire_et_convertir():
    # 1. Extraction du ZIP
    print(f"Extraction de {nom_zip}...")
    with zipfile.ZipFile(nom_zip, 'r') as zip_ref:
        zip_ref.extractall('temp_noise')

    chemin_geojson = os.path.join('temp_noise', fichier_geojson)

    # 2. Lecture du GeoJSON
    print("Lecture des données géographiques...")
    gdf = gpd.read_file(chemin_geojson)

    # 3. Traitement des données
    # Conversion UTC (ms) en format heure lisible
    gdf['Heure (UTC)'] = pd.to_datetime(gdf['leq_utc'], unit='ms').dt.strftime('%H:%M:%S')
    
    # Renommer pour correspondre à tes besoins
    gdf = gdf.rename(columns={'leq_mean': 'Niveau (leq_mean)'})

    # 4. Export vers Excel
    # On retire la colonne geometry pour l'export Excel
    df_excel = pd.DataFrame(gdf.drop(columns='geometry'))
    df_excel.to_excel(nom_excel_sortie, index=False)
    print(f"Fichier Excel créé : {nom_excel_sortie}")

    # 5. Génération du Tableau "Zoom sur un Choc"
    # On cherche le pic maximal pour centrer le zoom
    idx_max = gdf['Niveau (leq_mean)'].idxmax()
    
    # On prend une fenêtre de 3 secondes avant et 3 secondes après (7 secondes total)
    zoom_df = gdf.iloc[idx_max-3 : idx_max+4][['Heure (UTC)', 'Niveau (leq_mean)']].copy()

    # Ajout du constat visuel basé sur les niveaux
    def formater_constat(val):
        if val >= 80: return "!!! PIC CRITIQUE (Seuil de danger) !!!"
        if val >= 75: return "Nuisance forte (Poids lourd)"
        if val >= 70: return "Approche / Trafic intense"
        return "Bruit de fond"

    zoom_df['Constat visuel'] = zoom_df['Niveau (leq_mean)'].apply(formater_constat)

    print("\n" + "="*70)
    print("   GRAPHIQUE D'ÉMERGENCE : ZOOM SUR UN CHOC (PIC MAXIMAL)")
    print("="*70)
    print(zoom_df.to_string(index=False))
    print("="*70)
    print(f"Émergence calculée : {zoom_df['Niveau (leq_mean)'].max() - zoom_df['Niveau (leq_mean)'].min():.2f} dB(A)")

if __name__ == "__main__":
    extraire_et_convertir()