from argis.gis import GIS

from ..config import Config


def configure_profile(gis_url: str, config: Config, gis_profile: str, gis_username: str, gis_password: str) -> GIS:
    """
    Configures a named profile on the local machine using the provided credentials, and returns a GIS object authenticated with that profile.

    Parameters:
    - gis_url (str): The URL of the ArcGIS portal.
    - config (Config): The configuration object containing environment-specific settings.
    - gis_profile (str): The name of the profile to use.
    - gis_username (str): The username for the ArcGIS portal.
    - gis_password (str): The password for the ArcGIS portal.

    Returns:
    - GIS: An instance of the GIS class configured with the specified profile.
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