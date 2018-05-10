import requests
import ipykernel
import re
from notebook.notebookapp import list_running_servers


def get_current_notebook_filename():
    """Return the file containing the current notebook.

    Returns:
          notebook_path, relative to start dir of jupyter, example 'deliver/180501-NN-name.ipynb
    Notes:
        - 180510: Only tested on jupyterlab
        - Don't use this to copy the notebook file, unless you figure out a way to make sure it's saved first
    """
    for s0 in list_running_servers():
        r = requests.get(
            url=s0['url'] + 'api/sessions',
            headers={'Authorization': 'token {}'.format(s0['token']),})
        r.raise_for_status()
        response = r.json()
        kernel_id = re.search('kernel-(.*).json', ipykernel.connect.get_connection_file()).group(1)
        notebook_paths = {r['kernel']['id']: r['notebook']['path'] for r in response}
        if kernel_id in notebook_paths:
            return notebook_paths[kernel_id]
        else:
            continue # not found for this server
