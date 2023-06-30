import numpy as np
import pandas as pd
import yaml


def config_file_converter(fpath):
    sheetnames = ['Metadata','Independent Variables','Dependent Variables']
    data = {}
    for sheet in sheetnames:
        # read and format data
        data[sheet] = pd.read_excel(fpath, sheet_name=sheet, skiprows=1)

    ## Create yaml files
    out = {'attrs': {}, 'coords': {}, 'data_vars':{}}
    ret = {'classname': 'tsdat.io.retrievers.DefaultRetriever',
        'readers': {'.*': {'classname': 'tsdat.io.readers.CSVReader', 
                           'parameters': {'read_csv_kwargs': {'header':0, 
                                                              'index_col': False, 
                                                              'skiprows': 2}
                                         }
                          }
                    },
        'coords': {},
        'data_vars': {}}

    # Fetch attributes
    for item in data['Metadata'].columns:
        name = item.lower().replace(" ","_")
        out['attrs'].update({name: data['Metadata'][item].squeeze()})

    # Fetch coordinates
    dc = data['Independent Variables']
    dc['Standardized Unit'].replace(np.nan, "1", inplace=True)
    dc['Original Unit'].replace(np.nan, "1", inplace=True)
    dc['Long Name'].replace(np.nan,"", inplace=True)
    dc['Standard Name'].replace(np.nan,"", inplace=True)
    for i in dc.index:
        # Variable name
        coord = dc['New Name'][i].title()
        name = coord.lower().replace(" ","_")
        # Units
        unit = dc['Standardized Unit'][i]
        old_unit = dc['Original Unit'][i]
        # Dataset yaml setup
        out['coords'].update({name: {'dims': [name],
                                     'dtype': dc['Datatype'][i],
                                     'attrs': {'units': unit,
                                               'long_name': dc['Long Name'][i],
                                               'standard_name': dc['Standard Name'][i],
                                               },
                                    }
                             })
        # Retriever yaml setup
        ret['coords'].update({name: {'name': dc['Original Name'][i]}})
        # Add data converters
        if not unit == old_unit:
            if 'time' in name:
                d = {'data_converters': [{'classname': 'tsdat.io.converters.StringToDatetime',
                                          'format': old_unit,
                                          'timezone': dc['Timezone'][i],
                                          }]
                    }
            else:
                d = {'data_converters': [{'classname': 'tsdat.io.converters.UnitsConverter',
                                          'input_units': old_unit
                                          }]
                    }
            ret['coords'][name].update(d)

    # Fetch data variables
    dv = data['Dependent Variables']
    dv['Standardized Unit'].replace(np.nan, "1", inplace=True)
    dv['Original Unit'].replace(np.nan, "1", inplace=True)
    dv['Long Name'].replace(np.nan,None, inplace=True)
    dv['Standard Name'].replace(np.nan,None, inplace=True)
    dv['Description'].replace(np.nan,None, inplace=True)
    dv['Valid Minimum Value'].replace(np.nan, None, inplace=True)
    dv['Valid Maximum Value'].replace(np.nan, None, inplace=True)
    for i in dv.index:
        # Variable Name
        coord = dv['New Name'][i].title()
        name = coord.lower().replace(" ","_")
        # Units
        unit = dv['Standardized Unit'][i].replace('%','percent')
        old_unit = dv['Original Unit'][i].replace('%','percent')
        # Dataset yaml setup
        out['data_vars'].update({name: {'dims': dv['Dimensions'][i].replace(' ','').rsplit(','),
                                        'dtype': dv['Datatype'][i],
                                        'attrs': {'units': unit},
                                        }
                                })

        qc_vars = list(dv.columns[11:])
        var_list = ['long_name','standard_name','description','valid_min','valid_max'] + qc_vars
        attrs = dict.fromkeys(var_list)
        attrs['long_name'] = dv['Long Name'][i]
        attrs['standard_name'] = dv['Standard Name'][i]
        attrs['description'] = dv['Description'][i]
        attrs['valid_min'] = dv['Valid Minimum Value'][i]
        attrs['valid_max'] = dv['Valid Maximum Value'][i]
        for v in qc_vars:
            val = dv[v][i]
            if np.isnan(val):
                attrs[v] = None
            elif isinstance(val, float):  # number
                attrs[v] = float(val)
            else:  # string
                attrs[v] = val

        # Check type is compatibly with yaml format
        type_list = [str, int, np.ndarray, float, list, tuple]
        for v in var_list:
            if type(attrs[v]) in type_list:
                out['data_vars'][name]['attrs'].update({v: attrs[v]})

        # Retriever yaml setup
        ret['data_vars'].update({name: {'name': dv['Original Name'][i]}})
        # Add data converters
        if not unit == old_unit:
            ret['data_vars'][name].update({'data_converters': [{'classname': 'tsdat.io.converters.UnitsConverter',
                                                                'input_units': old_unit,
                                                                }]
                                        })


    with open('dataset.yaml','w') as file:
        yaml.dump(out, file) #  default_flow_style=None
    with open('retriever.yaml','w') as file:
        yaml.dump(ret, file) #  default_flow_style=None

    print('done')
