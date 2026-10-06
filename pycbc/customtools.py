from pycbc.workflow import WorkflowConfigParser
from pycbc.inference.models import read_from_config
import h5py
import numpy
def create_parser_from_injection(injection_file, data_file, model_file, **kwargs):
    """Create a WorkflowConfigParser instance that updates static_params section
    by reading it from the injection file.

    Inputs:
    "injection_file" : an hdf file containing only one injection
    "data_file" : a config file containing common data settings. The
    trigger-time and injection-file options will be updated using the
    provided injection.
    "model_file" : config file with the model settings. This also includes variable_params

    Output:
    "cp" : a workflow config parser
    """
    cp = WorkflowConfigParser([data_file, model_file])
    # Read the injection file to gather all the params
    all_params = {}
    with h5py.File(injection_file, 'r') as inj:
        for p in inj.keys():
            all_params[p] = inj[p][0]
        for sp in inj.attrs['static_args']:
            all_params[sp] = inj.attrs[sp]
    static_params = all_params.copy()
    # Remove the params included in the variable params
    for vp in cp['variable_params'].keys():
        static_params.pop(vp)
    # Create and add options to static_params section
    cp.add_section('static_params')
    for sp in static_params:
        cp.add_options_to_section('static_params',
                                  [(sp, str(static_params[sp]))])
    # Update options to data section
    cp.add_options_to_section('data',
                              [('trigger-time', str(static_params['tc'])),
                               ('injection-file', injection_file)])
    for key, value in kwargs.items():
        cp.add_options_to_section('model', [(key, str(value))])
    return cp

def loglr_surface(model,phi,custom_modes=None):
    shm,hmhn = model.inner_products(custom_modes)
    sh_phi = 0
    for m in shm:
        sh_phi+= numpy.real(shm[m]*numpy.exp(1j*m*phi))
    hh_cross = 0
    hh_self = 0
    for (m,n) in hmhn:
        if m==n:
            hh_self+=numpy.real(hmhn[(m,n)]/2)
        else:
            hh_cross+=numpy.real(hmhn[(m,n)]*numpy.exp(1j*(n-m)*phi))
    return sh_phi - hh_cross - hh_self

def gaussian_model_surface(model,phi):
    """  
    Returns the model evaluated at all points in phi
    """
    surface = numpy.zeros(len(phi))
    for (i,p) in enumerate(phi):
        model.update(coa_phase=p)
        surface[i]=model.loglr
    return surface
def create_model_from_injection(injection_file,data_config,model_config):
    """
    Custom function ONLY for the hm_marg model. Creates 
    and runs a dummy update so the methods in the model can be 
    used.
    Inputs:
    ----------------
    injection_file : the path to the injection file
    data_config : path to the config file containing data settings
    model_config : path the the config file specifying the model

    Ouputs:
    ---------------
    hm_model : an instantiated HMPhaseMarginalize object  
    """
    hm_model = read_from_config(
    create_parser_from_injection(
        injection_file=injection_file,
        data_file=data_config,
        model_file=model_config
        )
    )
    hm_model.update(coa_phase=0) ##HACK: To update params in current params. Does not change any behaviour
    return hm_model
