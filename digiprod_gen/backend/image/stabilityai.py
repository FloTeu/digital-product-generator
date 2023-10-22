import os
from stability_sdk import client
import streamlit as st

def set_env_variables():
    # Our Host URL should not be prepended with "https" nor should it have a trailing slash.
    os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'

def get_upscaling_client(upscale_engine="esrgan-v1-x2plus"):
    # Set up our connection to the API.
    return client.StabilityInference(
        key=st.secrets["api_token"]["stability_ai"],  # API Key reference.
        upscale_engine=upscale_engine,  # The name of the upscaling model we want to use.
        # Available Upscaling Engines: esrgan-v1-x2plus, stable-diffusion-x4-latent-upscaler
        verbose=True,  # Print debug messages.
    )