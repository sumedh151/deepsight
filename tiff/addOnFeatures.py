import rasterio
import earthpy as et

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
    
#     print(proj4)
#     print(sat_data.crs.wkt)
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
    

# print(metadata(img))