from arcgis.gis import GIS

from ..config import Config


def configure_gis_profile(gis_url: str, config: Config, gis_profile: str, gis_username: str, gis_password: str) -> GIS:
    """
    Configure a local ArcGIS profile and return an authenticated GIS object.

    Args:
        gis_url: URL of the ArcGIS portal.
        config: Configuration object containing optional environment-specific settings.
        gis_profile: Name of the ArcGIS profile to use.
        gis_username: ArcGIS username.
        gis_password: ArcGIS password.

    Returns:
        GIS: GIS instance authenticated with the configured profile.

    Raises:
        ValueError: If config is not a Config instance.
        ValueError: If required values are missing after resolving inputs.
        ValueError: If any resolved parameter is not a string.
    """
    # require either config with gis_url, gis_profile, gis_username, and gis_password, or all 4 parameters passed directly to the function
    if config is not None:

        # ensure object is of type Config
        if not isinstance(config, Config):
            raise ValueError("Config parameter must be an instance of the Config class.")
        
        # attempt to pull values from config if they exist
        gis_url = config.get("esri.gis_url", default=gis_url)
        gis_profile = config.get("esri.gis_profile", default=gis_profile)
        gis_username = config.get("esri.gis_username", default=gis_username)
        gis_password = config.get("esri.gis_password", default=gis_password)

        if not all([gis_url, gis_profile, gis_username, gis_password]):
            raise ValueError("All parameters (gis_url, gis_profile, gis_username, gis_password) must be provided either through the config object or directly to the function.")
    
    # ensure all parameters are provided at this point (either through config or directly)    
    if not all([gis_url, gis_profile, gis_username, gis_password]):
        raise ValueError("All parameters (gis_url, gis_profile, gis_username, gis_password) must be provided either through the config object or directly to the function.")
    
    # ensure all parameters are strings
    if not all(isinstance(param, str) for param in [gis_url, gis_profile, gis_username, gis_password]):
        raise ValueError("All parameters (gis_url, gis_profile, gis_username, gis_password) must be of type string.")
    
    # create the profile by instantiating a GIS object with the provided credentials and profile name; this will create the profile if it doesn't already exist, or overwrite it if it does
    gis = GIS(url=gis_url, profile=gis_profile, username=gis_username, password=gis_password)

    return gis