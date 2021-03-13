import rasterio
import earthpy as et
import numpy as np

# Metadata of satellite image
# input : image
# output : dict of meta data
def metadata(img):
    """
        Metadata of satellite image
    """
    sat_data = rasterio.open(img)
    
    # Meta Data
    meta_data = sat_data.meta
    
    #   Width and Height in projected units
    width_in_projected_units = sat_data.bounds.right - sat_data.bounds.left
    height_in_projected_units = sat_data.bounds.top - sat_data.bounds.bottom
    
    
    #   Converting the pixel co-ordinates to longitudes and latitudes
    # Upper left pixel
    row_min = 0
    col_min = 0

    # Lower right pixel.  Rows and columns are zero indexing.
    row_max = sat_data.height - 1
    col_max = sat_data.width - 1

    # Transform coordinates with the dataset's affine transformation.
    topleft = sat_data.transform * (row_min, col_min)
    botright = sat_data.transform * (row_max, col_max)
    
    # Coordinate Reference System 
    proj4 = et.epsg[sat_data.crs.to_dict()['init'].split(':')[-1]]
    
    sat_data.close()
    
    return {
        "metadata" : meta_data, 
        "projected_units" : {"width" : width_in_projected_units, "height" : height_in_projected_units},
        "bounds" : sat_data.bounds,
        "coords" : {
            "topleft" : topleft,
            "bottomright" : botright,
        },
        "proj4" : proj4,
        "wkt" : sat_data.crs.wkt,
    }
    


def vegetationIndices(sat_data):
    """
        Calculates different vegetation indices
    """

    vegetation_indices = {}
    
    #    Normalized Difference Vegetation Index (NDVI)
    r = sat_data.read(3)
    nir = sat_data.read(7)
    
    vegetation_indices.update({"Normalized Difference Vegetation Index" : np.divide(np.add(nir, r), np.subtract(nir, r))})

    L = 0.5
    vegetation_indices.update({
        "Soil Adjusted Vegetation Index" : ((sat_data.read(7) - sat_data.read(3)) / (sat_data.read(7) + sat_data.read(3) + L)) * (1 + L)
    })

    #     Visible Atmospherically Resistant Index
    vegetation_indices.update({
        "Visible Atmospherically Resistant Index" : (sat_data.read(2) - sat_data.read(3))/ (sat_data.read(2) + sat_data.read(3) - sat_data.read(1))
    })
    return vegetation_indices


def waterIndices(sat_data) :
    """
        Calculates different water indices
    """
    
    water_indices = {}

    #     Modified Normalized Difference Water Index (MNDWI)
    water_indices.update({"Modified Normalized Difference Water Index" : np.divide(np.subtract(sat_data.read(2), sat_data.read(10)), np.add(sat_data.read(2), sat_data.read(10))) })
    
    #     Normalized Difference Moisture Index (NDMI)
    water_indices.update({"Normalized Difference Moisture Index" : np.divide(np.subtract(sat_data.read(7), sat_data.read(10)), np.add(sat_data.read(7), sat_data.read(10))) })
    
    return water_indices

def geologyIndices(sat_data):
    """
        Calculates different geology indices
    """
    
    geology_indices = {}
    
    #     Clay Minerals Ratio
    geology_indices.update({"Clay Minerals Ratio" : np.divide(sat_data.read(10), sat_data.read(11))})
    
    #     Ferrous Minerals Ratio
    geology_indices.update({"Ferrous Minerals Ratio" : np.divide(sat_data.read(10), sat_data.read(7))})
    
    return geology_indices


def addOnFeatureIndices(img, img_class):
    """
        Calculates and returns vegetation, water and geology indices
        img and img_class required as input
        img_class is a string obj
    """
    indices = {}
    
    sat_data = rasterio.open(img)
    if img_class != "River" and img_class != "SeaLake" and img_class != "Industrial" and img_class != "Highway" :
        indices.update({"Vegetation Indices" : vegetationIndices(sat_data)})
    
    indices.update({"Water Indices" : waterIndices(sat_data)})
    indices.update({"Geology Indices" : geologyIndices(sat_data)})
    
    sat_data.close()
    return indices
