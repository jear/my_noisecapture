import geopandas as gpd
import pandas as pd

try:
    # Chargement
    gdf = gpd.read_file('track.geojson')
    
    # Extraction des coordonnées pour Excel
    gdf['longitude'] = gdf.geometry.x
    gdf['latitude'] = gdf.geometry.y
    
    # Conversion UTC en format Lisible (Optionnel mais recommandé)
    # On divise par 1000 car NoiseCapture est en millisecondes
    gdf['heure_lisible'] = pd.to_datetime(gdf['leq_utc'], unit='ms')
    
    # Suppression de la colonne géométrique brute pour Excel
    df = pd.DataFrame(gdf.drop(columns='geometry'))
    
    # Export
    df.to_excel('donnees_rue_saint_romain.xlsx', index=False)
    print("Succès ! Votre fichier Excel est prêt.")

except Exception as e:
    print(f"Erreur lors de la conversion : {e}")