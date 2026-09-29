from pycbc.workflow import WorkflowConfigParser
import h5py


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