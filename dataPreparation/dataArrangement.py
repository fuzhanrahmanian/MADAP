'''' This file serves to transfer all the data in the json format into a pandas dataframe. '''

import pandas as pd
import numpy as np
from glob import glob # https://docs.python.org/3/library/glob.html
from tqdm import tqdm # https://tqdm.github.io/
import json
import os

os.chdir(r'C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data')

## Define savepath for dataframe of raw data
dataFolder = r"C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data"
savepath = r'C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data'


# # #######################################################################
# # ### Step 1 - transferring all the data from the json to a dataframe ###
# # #######################################################################

# ## Define relevant funcitons

# def keyToLabel(key:str):
#     ''' This function makes the key lower case and removes spaces while making it camel case.'''
#     fragments = key.split(' ')
#     for i in range(len(fragments)):
#         if '-' in fragments[i]:
#             pass
#         else:
#             if i == 0:
#                 fragments[i] = f'{fragments[i][0].lower()}{fragments[i][1:]}'
#             else:
#                 fragments[i] = fragments[i].capitalize()
#     label = ''.join(fragments)
#     return label

# def iterateKeys(coll:dict):
#     collectionResults = {}
#     for key in coll.keys():
#         resultKey = keyToLabel(key)
#         if type(coll[key]) == dict:
#             preKey = f'{resultKey}-'
#             for k in coll[key].keys():
#                 newKey = f'{preKey}{keyToLabel(k)}'
#                 collectionResults[newKey] =coll[key][k]
#         elif (type(coll[key]) == list):
#             if (type(coll[key][0]) == dict):
#                 for i in range(len(coll[key])):
#                     preKey = f'{resultKey}{i}-'
#                     for j in coll[key][i].keys():
#                         newKey = f'{preKey}{keyToLabel(j)}'
#                         collectionResults[newKey] = coll[key][i][j]
#             # if the element is not a list of dicts
#             else: 
#                 collectionResults[resultKey] = coll[key]
#         else:
#             collectionResults[resultKey] = coll[key]
#     return collectionResults

# ## Extract the data from the json and write it to the dataframe

# # Initialize a pandas dataframe to collect all the data
# coll = pd.DataFrame()

# # Go through all files in the folder dataFolder
# for filepath in tqdm(glob(dataFolder+"/*.json")):
#     with open(filepath, "r") as fp:
#         data = json.load(fp)

#     # generate a dict with keys without spaces
#     coll_individual_dict = iterateKeys(data)

#     # iterate several times to make sure no dicts or lists remain as values
#     for i in range(3):
#         # check for any dict or list in the values
#         typesDict = [type(coll_individual_dict[k]) == dict for k in coll_individual_dict.keys()]
#         typesList = [type(coll_individual_dict[k]) == list for k in coll_individual_dict.keys()]
#         # if any dict or list is found, repeat the iteration process
#         if any(typesDict) or any(typesList):
#             coll_individual_dict = iterateKeys(coll_individual_dict)
#         # otherwise break the loop
#         else:
#             break
#     # print(coll_individual)
    
#     # convert the results for the individual file to a dataframe
#     coll_individual = pd.DataFrame(index=range(1), columns=coll_individual_dict.keys())#coll_individual_dict, index=range(1))
#     for c in coll_individual_dict.keys():
#         coll_individual.at[0, c] = coll_individual_dict[c]
#     coll_individual.at[0,'fileName'] = str(filepath.split('\\')[-1])

#     # concatenate the individual result with the collected results
#     coll = pd.concat([coll, coll_individual], axis=0, ignore_index=True)

# # save the collected Data to a csv file
# coll.to_csv(f'{savepath}/Dataframe_all508.csv', sep=';')


# #############################################
# ### Step 2 - Getting a filtered dataframe ###
# #############################################

# # Get the flattened json dataframe
# startFrame0 = pd.read_csv(f'{savepath}/Dataframe_all508.csv', sep=';', index_col='Unnamed: 0')
# print(startFrame0)
# #startFrame0 = cudf.DataFrame.from_pandas
# # Initiate a new dataframe to collect the results
# newFrame = pd.DataFrame(columns=['experimentID', 'temperature [°C]', 'resistance [Ohm]', 'conductivity [S/cm]', 'amplitude [-]', 'frequency [Hz]', "real impedance Z' [Ohm]", "imaginary impedance Z'' [Ohm]", 'cell constant, standard deviation', 'bias', 'error', 'GD', 'range', 'PC [g]', 'EC [g]', 'EMC [g]', 'LiPF6 [g]', 'metadata'])

# # Go through all the files/rows in the start dataframe
# for filename in tqdm(startFrame0['fileName'].unique()):
#     print(filename)
#     # Get only the data corresponding to one json file
#     startFrame = startFrame0.loc[startFrame0['fileName'] == filename]

#     # Generate a dataframe for only one json file
#     newFrame2 = pd.DataFrame(columns=['experimentID', 'temperature [°C]', 'resistance [Ohm]', 'conductivity [S/cm]', 'amplitude [-]', 'frequency [Hz]', "real impedance Z' [Ohm]", "imaginary impedance Z'' [Ohm]", 'cell constant, standard deviation', 'bias', 'error', 'GD', 'range', 'PC [g]', 'EC [g]', 'EMC [g]', 'LiPF6 [g]', 'metadata'])
#     # Initiate the dictionary for the metadata
#     metadata = {'experimentDate': startFrame['conductivityExperiment-experimentDate'].values[0],
#                 'experimentType': startFrame['experimentType'].values[0],
#                 'formatVersion': startFrame['formatVersion'].values[0],
#                 'channel': startFrame['conductivityExperiment-channel'].values[0],
#                 'electrolyteAmount [µL]': startFrame['conductivityExperiment-electrolyteAmount'].values[0],
#                 'suspectedMeasurementError': startFrame['conductivityExperiment-suspectedMeasurementError'].values[0],
#                 'PC':{},
#                 'EC':{},
#                 'EMC':{},
#                 'LiPF6':{}}

#     # Go through all the columns in the start dataframe
#     for c in startFrame.columns:
#         # Check for the arrhenius data
#         if 'arrhenius' in c:
#             # Get the temperature values and put the im newFrame2
#             if ('temperature' in c) and ('data' in c):
#                 newFrame2['temperature [°C]'] = eval(startFrame[c].values[0])
#             # Get the resistance values and put them in newFrame2
#             if ('resistance' in c) and ('data' in c):
#                 newFrame2['resistance [Ohm]'] = eval(startFrame[c].values[0])
#         # Collect all the data corresponding to the impedance data and sort it into newFrame2
#         if ('impedanceData' in c) and ('comment' not in c) and ('temperature' not in c):
#             split = c.split('-')
#             split_exceptLast2 = split[0:-2]
#             label_exceptLast2 = '-'.join(split_exceptLast2)
#             for x in ['amplitude', 'bias', 'err', 'frequency', 'gD', 'range', "z'", "z''"]:
#                 # Replacements due to discrepancies between newFrame2 and startFrame column keys
#                 if x == 'gD':
#                     x2 = 'GD'
#                 elif x == "z'":
#                     x2 = "Z'"
#                 elif x == "z''":
#                     x2 = "Z''"
#                 else:
#                     x2 = x
#                 colFrame2 = [a for a in newFrame2.columns if (x2 in a)]
#                 # This is necessary due to different structures of the json files
#                 if np.isnan(startFrame[f'{label_exceptLast2}-temperature'].values[0]):
#                     temp = startFrame[f'{label_exceptLast2}-temperature-temperature']
#                 else:
#                     temp = startFrame[f'{label_exceptLast2}-temperature']
#                 newFrame2.loc[newFrame2['temperature [°C]'] == temp.values[0], colFrame2[0]] = startFrame[f'{label_exceptLast2}-{x}-data'].values[0]
#         # Add the conductivity to newFrame2
#         if ('conductivityData' in c) and ('conductivity-data' in c):
#             newFrame2['conductivity [S/cm]'] = eval(startFrame[c].values[0])
#         # Add the cell constant and its standard deviation to newFrame2
#         if ('cellConstant' in c):
#             split = c.split('-cellConstant')
#             start = split[0]
#             if np.isnan(startFrame[f'{start}-cellConstantStandardDeviation'].values[0]):
#                 standarddev = 0.0
#             else:
#                 standarddev = startFrame[f'{start}-cellConstantStandardDeviation'].values[0]
#             t = (startFrame[f'{start}-cellConstant'].values[0], standarddev)
#             # Repeat the values to get full rows
#             list_t = [t for i in range(len(newFrame2['cell constant, standard deviation']))]
#             newFrame2['cell constant, standard deviation'] = list_t
#         # Add the data concerning the electrolyte components
#         if ('electrolyteComponent' in c) and ('acronym' in c):
#             for acronym in startFrame[c].unique():
#                 if type(acronym) == str:
#                     split = c.split('-')
#                     labelFirst = '-'.join(split[:-1])
#                     # Repeat the values to get full rows
#                     list_amount = [startFrame[f'{labelFirst}-amount'].values[0] for i in range(len(newFrame2[f'{acronym} [g]']))]
#                     newFrame2[f'{acronym} [g]'] = list_amount
#         # Put the metadata concerning the electrolyte components to the metadata dictionary
#         if ('electrolyteComponent' in c) and ('acronym' not in c):
#             split = c.split('-')
#             lastLabel = -1
#             if ('amount' not in c) and ('amountUnit' not in c):
#                 if ('Batch' in c) or ('CAS' in c):
#                     lastLabel = -2
#                 labelLast = '-'.join(split[lastLabel::])
#                 acronymLabel1 = '-'.join(split[:lastLabel])
#                 acronymLabel = f'{acronymLabel1}-acronym'
#                 acronym = startFrame[acronymLabel].unique()[0]
#                 if type(acronym) == str:
#                     metadata[acronym][labelLast] = startFrame[c].values[0]

#     # Add the metadata to the dataframe
#     # Repeat the values to get full rows
#     metaData = [metadata for i in range(len(newFrame2['metadata']))]
#     newFrame2['metadata'] = metaData
#     # Add the experiment ID to the dataframe
#     # Repeat the values to get full rows
#     expID = [startFrame['experimentId'].values[0] for i in range(len(newFrame2['experimentID']))]
#     newFrame2['experimentID'] = expID

#     # Append the dataframe for one file to the dataframe collecting the results for all files
#     newFrame = pd.concat([newFrame, newFrame2], axis=0, ignore_index=True)

#     # Set all missing values to zero
#     newFrame.fillna(value=0.0, inplace=True)

# # Save the dataframe to csv file
# newFrame.to_csv(f'{savepath}/Dataframe_STRUCTURED_all508.csv', sep=';')




# #######################################################################
# ### Step 2 - joining columns in the dataframe to yield full columns ###
# #######################################################################

# startFrame = pd.read_csv(f'{savepath}/Dataframe_all363.csv', sep=';', index_col='Unnamed: 0')


# startFrame = startFrame.loc[startFrame['fileName'] == 'Conductivity_WOC_02112021_BM247_2_Channel_l2.json']

# columns = []
# indexCandidates = []
# startcols = startFrame.columns
# #print('\n STARTcols', startFrame.columns)
# for col in startFrame.columns:
#     colSplit = col.split('-')
#     if ('Unit' in colSplit[-1]):
#         ending = 'unit'
#         secondLast = colSplit[-1].split('U')[0]
#         colSplit = colSplit[0:-1] + [secondLast, ending]
#     # if ('Amount' in colSplit[-1]):
#     #     ending = 'amount'
#     #     secondLast = colSplit[-1].split('A')[0]
#     #     colSplit = colSplit[0:-1] + [secondLast, ending]
#     elif (colSplit[-1] in ['temperature', 'amount', 'molarMass', 'substanceAmount']) and (colSplit[-2] not in ['temperature', 'amount', 'molarMass', 'substanceAmount']):
#         colSplit.append('data')
#     elif (colSplit[-1] in ['temperature', 'amount', 'molarMass', 'substanceAmount']) and (colSplit[-2] in ['temperature', 'amount', 'molarMass', 'substanceAmount']):
#         colSplit[-1] = 'data'
#     if (colSplit[-1] not in columns):
#         columns.append(colSplit[-1])
#     if len(colSplit[0:-1]) < 3:
#         colSplitSelection = colSplit[0:-1].copy()
#         for j in range(3 - len(colSplit[0:-1])):
#             colSplitSelection.append('not_here')
#             colSplitNew = colSplitSelection
#     else:
#         colSplitNew = colSplit[0:-1]
#     if colSplitNew not in indexCandidates:
#         indexCandidates.append(colSplitNew)
    
# indices = np.array(indexCandidates).reshape((len(indexCandidates), 3))
# newFrame = pd.DataFrame(columns=columns)
# newFrame['index0'] = indices[:, 0]
# newFrame['index1'] = indices[:, 1]
# newFrame['index2'] = indices[:, 2]
# newFrame.set_index(['index0', 'index1', 'index2'], inplace=True)

# newstartcols = startFrame.columns
# #print('\n NEWstartCOLS', startFrame.columns)
# print(all(newstartcols==startcols))
# for column in startFrame.columns:
#     #print('COLUMN', column)
#     split = column.split('-')
#     if ('Unit' in split[-1]):
#         ending = 'unit'
#         secondLast = split[-1].split('U')[0]
#         split = split[0:-1] + [secondLast, ending]
#     # if ('Amount' in split[-1]):
#     #     ending = 'amount'
#     #     secondLast = split[-1].split('A')[0]
#     #     split = split[0:-1] + [secondLast, ending]
#     elif (split[-1] in ['temperature', 'amount', 'molarMass', 'substanceAmount']) and (split[-2] not in ['temperature', 'amount', 'molarMass', 'substanceAmount']):
#         split.append('data')
#     elif (split[-1] in ['temperature', 'amount', 'molarMass', 'substanceAmount']) and (split[-2] not in ['temperature', 'amount', 'molarMass', 'substanceAmount']):
#         split[-1] = 'data'
#     if len(split) < 4:
#         splitPart = split[0:-1]
#         for n in range(4 - len(split)):
#             splitPart.append('not_here')
#         split = splitPart + [split[-1]]
#     if (type(startFrame[column].values[0]) == str) and ('[' in startFrame[column].values[0]) and not ('[Li]' in startFrame[column].values[0]):
#         value = eval(startFrame[column].values[0])
#         newFrame[split[-1]].astype(object)
#     else:
#         value = startFrame[column].values[0]
#     print('startframeCOL', column, startFrame[column].values[0], value)
#     newFrame.at[(split[0], split[1], split[2]), split[-1]] = value
# newFrame = newFrame.transpose()
# newFrame.to_csv(f'{savepath}/Dataframe_levels_all363.csv', sep=';')
# #newFrame = newFrame.explode('data')
# #print(newFrame['data'])

# newFrame2 = pd.DataFrame(columns=['temperature [°C]', 'resistance [Ohm]', 'conductivity [S/cm]', 'amplitude [-]', 'frequency [Hz]', "real impedance Z' [Ohm]", "imaginary impedance Z'' [Ohm]", 'cell constant, standard deviation', 'bias', 'error', 'GD', 'range', 'PC [g]', 'EC [g]', 'EMC [g]', 'LiPF6 [g]', 'VC [g]', 'metadata'])

# for c in newFrame.columns:
#     if type(newFrame.loc['data', c])==list:
#         if any(['temperature' in x.lower() for x in c]):
#             if any(['arrhenius' in x.lower() for x in c]):
#                 newFrame2['temperature [°C]'] = newFrame.loc['data', c]
#             # if any(['impedanceData' in x for x in c]):
#             #     print(newFrame.loc['data', c].values)
#                 #newFrame2.loc[newFrame2['temperature [°C]'] == newFrame.loc['data', c].values, 'amplitude [-]'] = str(newFrame.loc['data', (c[0], c[1], 'amplitude')])
#                 #print('Hello', newFrame2.loc[newFrame2['arrhenius temperature [°C]'] == newFrame.loc['data', c], 'arrhenius temperature [°C]'])
#         if any(['resistance' in x.lower() for x in c]):
#             newFrame2['resistance [Ohm]'] = newFrame.loc['data', c]
#         if any(['conductivity' in x.lower() for x in c]):
#             newFrame2['conductivity [S/cm]'] = newFrame.loc['data', c]
#         # if any(['amplitude' in x.lower() for x in c]):
#         #     newFrame2['amplitude [-]'] = newFrame.at['data', c]
#         # if any(['frequency' in x.lower() for x in c]):
#         #     newFrame2['frequency [-]'] = newFrame.loc['data', c]

# print(newFrame2)

# # columnsIndexNewFrame = newFrame.columns.to_frame(index=False) # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.MultiIndex.to_frame.html
# # columnsIndexNewFrame.replace(to_replace='not_here', value=np.NaN, inplace=True) # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
# # print(columnsIndexNewFrame)

# # newFrame2['quantity'] = columnsIndexNewFrame['index2'].dropna().unique()
# # print(newFrame2)
# # for col in newFrame.columns:
# #     newFrame.loc['quantity'] = 


# ##########################################################################################################
# ### Step 3 - remove columns with redundant information and put the information into the columns labels ###
# ##########################################################################################################

# ## TODO:
# # join the columns in a reasonable way
# # select a useful multiindex
# # in a second step:  put the units in the column names


#############################################
### Step 3 - Describe the resulting table ###
#############################################

## Load the dataframe containing the data
filepath = r'C:\Repositories\MADAP\data\final_version_10.csv' # f'{savepath}/Dataframe_STRUCTURED_all508.csv'
table = pd.read_csv(filepath, sep=';', index_col='Unnamed: 0')
# table.to_hdf(f'{savepath}/Dataframe_STRUCTURED_all508.hdf', key='electrolyte_data')
# table = pd.read_hdf(f'{savepath}/Dataframe_STRUCTURED_all508.hdf')

## separate the column label from the unit and the symbol
colLabels = ['_'.join(c.split(' ')[:-1]) if '[' in c.split(' ')[-1] else '_'.join(c.split(' ')) for c in table.columns]
colLabels = [cl if (not ('impedance_Z' in cl)) and (not ('phase' in cl)) else '_'.join(cl.split('_')[:-1]) for cl in colLabels]

# remove the evaluation from the json
del table['resistance [Ohm]']
del table['conductivity [S/cm]']
# remove the entries irrelevant for the dataset
del table['marker']
del table['mapped_temp']
del table['edgecolor']
del table['EC/PC [gr/gr]']
del table['madap_eis_fit']

colLabels = [cl for cl in colLabels if cl not in ['resistance', 'conductivity', 'marker', 'mapped_temp', 'edgecolor', 'EC/PC', 'madap_eis_fit']]

# replace the column labels by the paper ones
for i in range(len(colLabels)):
    if 'madap' in colLabels[i]:
        if 'eis_conductivity' in colLabels[i]:
            colLabels[i] = 'EIS_conductivity'
        elif 'fit_params' in colLabels[i]:
             colLabels[i] = 'EIS_fittedParameters'
        elif 'rmse' in colLabels[i]:
             colLabels[i] = 'EIS_RMSE'
        elif 'num_rc_linKK' in colLabels[i]:
             colLabels[i] = 'EIS_numberRCelements'
        elif 'resistance' in colLabels[i]:
             colLabels[i] = 'EIS_resistance'
        elif 'chi_square' in colLabels[i]:
             colLabels[i] = 'EIS_chiSquare'
        elif 'eval_fit' in colLabels[i]:
             colLabels[i] = 'EIS_fitEvaluation'
        elif 'impedance' in colLabels[i]:
             colLabels[i] = 'EIS_impedance'
        elif 'residual_real' in colLabels[i]:
             colLabels[i] = 'EIS_residualReal'
        elif 'residual_imaginary' in colLabels[i]:
             colLabels[i] = 'EIS_residualImaginary'
        elif 'activation_energy' in colLabels[i]:
             colLabels[i] = 'Arrhenius_activationEnergy'
        elif 'activation_constant' in colLabels[i]:
             colLabels[i] = 'Arrhenius_preExponential'
        elif 'activation_r2_score' in colLabels[i]:
             colLabels[i] = 'Arrhenius_R2'
        elif 'activation_mse' in colLabels[i]:
             colLabels[i] = 'Arrhenius_MSE'
        elif 'fitted_log_conductivity' in colLabels[i]:
             colLabels[i] = 'Arrhenius_logConductivity'
        elif 'custom_circuit' in colLabels[i]:
            colLabels[i] = 'EIS_circuit'
symbolsDict = {'temperature': 'T', 'resistance': 'R', 'conductivity': r'\sigma', 'frequency': 'f', 'real_impedance': "Z'", 'imaginary_impedance': "Z''", 'phase_shift': 'φ'}
colSymbols = [symbolsDict[c] if c in symbolsDict.keys() else '-' for c in colLabels]
colUnits = [c.split(' ')[-1].strip('[').strip(']') if '[' in c.split(' ')[-1] else '-' for c in table.columns]

colIndex = pd.MultiIndex.from_arrays([colLabels, colSymbols, colUnits], names=['label', 'symbol', 'unit'])

table.columns = colIndex

## Remove all zero columns
for c in table.columns.get_level_values('label'):
    # get all the index levels for the column label
    otherColLabels = table.columns.get_loc_level(c)[1][0]
    # assemble them to the full index in order to get a pd.Series as an output after indexing
    cTotal = (c, otherColLabels[0], otherColLabels[1])
    # if the column contains only one unique value and if this values is zero, remove the column from the dataframe
    if (len(table[cTotal].unique()) == 1):
        try:
            if ((table[cTotal].unique() == 0) or (table[cTotal].unique()[0][1] == '0')):
                del table[cTotal]
        except IndexError:
            pass

# save the reduced dataframe as csv for checking
table.to_csv(f'{savepath}/finalised_reduced.csv', sep=';')

## Initialize the dataframe to collect the description
tableDescription = pd.DataFrame(index=table.columns.get_level_values('label'), columns=['Description', 'Data type', 'Range', 'Unique entries', 'Units'])
tableDescription.index.name = 'Column name' # https://stackoverflow.com/questions/37968730/set-index-name-of-pandas-dataframe

## Get a string of all but the last key of the metadata dictionary
# define nan so it can be evaluated
nan = np.NaN
metadataKeys = list(eval(table.at[0,('metadata','-','-')]).keys())
# join all keys but the last to enable insertion of 'and' in the description
metadataKeysStr = ', '.join(metadataKeys[0:-1])

descriptions = {
    'experimentID': 'a unique identifyer for each experiment coding an operator, the date of the experiment and the batch of the electrolyte used.',
    'temperature': 'the temperature at which the measurement was taken',
    'resistance': 'resistance obtained from electrochemical impedance data',
    'conductivity': 'conductivity obtained as the inverse of the resistance obtained from electrochemical impedance data',
    'amplitude': 'a series of amplitude values selected for the electrochemical impedance spectroscopy',
    'frequency': 'a series of frequency values selected for the electrochemical impedance spectroscopy',
    'real_impedance': 'a series of the real part of the impedance measured during the electrochemical impedance spectroscopy',
    'imaginary_impedance': 'a series of the imaginary part of the impedance measured during the electrochemical impedance spectroscopy',
    'cell_constant,_standard_deviation': 'a tuple comprising the cell constant and its standard deviation determined from five measurements using a 0.01 M KOH standard solution at 20 °C with a 2 h equilibration period between measurements',
    'PC': 'the mass of propylene carbonate (PC) used when formulating the electrolyte solution',
    'EC': 'the mass of ethylene carbonate (EC) used when formulating the electrolyte solution',
    'EMC': 'the mass of ethyl methyl carbonate (EMC) used when formulating the electrolyte solution',
    'LiPF6': 'the mass of lithium hexafluorophosphate (LiPF6) used when formulating the electrolyte solution',
    'metadata': f'further metadata regarding the electrolyte solution arranged in a dictionary with the keys {metadataKeysStr}, and {metadataKeys[-1]}',
    'phase_shift': 'the phase shift as obtained from EIS analysis as implemented in \\textit{MADAP}',
    'EIS_chiSquare': 'a statistical measure for the goodness of the fit as obtained from the linKK method as implemented in the \\textit{impedance} package~\cite{Murbach2020}',
    'EIS_conductivity': 'the conductivity as obtained from EIS analysis performed using \\textit{MADAP}',
    'EIS_circuit': 'the equivalent circuit for the EIS spectrum as obtained from the linKK method as implemented in the \\textit{impedance} package~\cite{Murbach2020}',
    'EIS_optimalNumberRCelements': 'the optimum number of RC elements in the equivalent circuit needed to reproduce the EIS spectrum determined using the linKK method as implemented in the \\textit{impedance} package~\cite{Murbach2020}',
    'EIS_fitEvaluation': 'a numeric value indicating the quality of the fit. A value close to unity indicates a good fit.',
    'EIS_fittedParameters': 'the values and corresponding uncertainties of the elements in the equivalend circuit as determined using \\textit{MADAP}',
    'EIS_numberRCelements': 'the required number of RC elements in the equivalent circuit required to reproduce the EIS spectrum determined using the linKK method as implemented in the \\textit{impedance} package~\cite{Murbach2020}',
    'EIS_impedance': 'a list of impedance values obtained from the fit generated during the EIS analysis performed using \\textit{MADAP}',
    'EIS_residualImaginary': 'the imaginary part of the residuals of the fit as determined using the linKK method as implemented in the \\textit{impedance} package~\cite{Murbach2020}',
    'EIS_residualReal': 'the real part of the residuals of the fit as determined using the linKK method as implemented in the \\textit{impedance} package~\cite{Murbach2020}',
    'EIS_resistance': 'the ionic charge transfer resistance as obtained from EIS analysis as implemented in \\textit{MADAP}',
    'EIS_RMSE': 'the RMSE of the fit obtained by applying the equivalent circuit determined using \\textit{MADAP} in the real and imaginary dimension ',
    'Arrhenius_activationEnergy': 'the activation energy obtained from the analysis according to the Arrhenius equation using \\textit{MADAP}',
    'Arrhenius_preExponential': 'the pre-exponential factor obtained from the analysis according to the Arrhenius equation using \\textit{MADAP}',
    'Arrhenius_R2': 'the $R^{2}$ score corresponding to the linear fit obtained in the analysis according to the Arrhenius equation using \\textit{MADAP}',
    'Arrhenius_MSE': 'the mean square error for the linear fit determined during the analysis according to the Arrhenius equation using \\textit{MADAP}',
    'Arrhenius_logConductivity': 'a list of $log(\sigma)$ obtained from the linear fit according to the Arrhenius equation determined by \\textit{MADAP}'
}

typesTranslation = {
    "<class 'str'>": 'string',
    "<class 'dict'>": {"<class 'str'>": 'Str[Dict[str]]', "<class 'tuple'>": 'Str[Dict[tuple]]'},
    "<class 'list'>": {"<class 'str'>": 'Str[List[str]]', "<class 'tuple'>": 'Str[List[tuple]]', "<class 'float'>": 'Str[List[float]]', "<class 'int'>": 'Str[List[int]]', "<class 'complex'>": 'Str[List[compex]]'},
    "<class 'tuple'>": {"<class 'str'>": 'Str[Tuple[str]]', "<class 'float'>": 'Str[Tuple[float]]', "<class 'int'>": 'Str[Tuple[int]]'},
    "float64": 'float'
}

for column in table.columns.get_level_values('label'):
    # get the full column index
    otherColIndices = table.columns.get_loc_level(column)[1][0]
    columnTotal = (column, otherColIndices[0], otherColIndices[1])
    # fill in the description of the data in each column
    tableDescription.at[column, 'Description'] = descriptions[column]
    # fill in the data type for each column
    if table.dtypes[columnTotal] == np.object_:
        try:
            dataType = type(eval(table[columnTotal][0]))
            if all([type(eval(e)) == dataType for e in table[columnTotal]]) and (str(dataType) != "<class 'dict'>"):
                tableDescription.at[column, 'Data type'] = typesTranslation[str(dataType)][str(type(eval(table[columnTotal][0])[0]))]
            elif all([type(eval(e)) == dataType for e in table[columnTotal]]) and (str(dataType) == "<class 'dict'>"):
                tableDescription.at[column, 'Data type'] = typesTranslation[str(dataType)][str(type(eval(table[columnTotal][0])[list(eval(table[columnTotal][0]).keys())[0]]))]
        except NameError:
            dataType = type(table[columnTotal][0])
            tableDescription.at[column, 'Data type'] = typesTranslation[str(dataType)]
    else:
        tableDescription.at[column, 'Data type'] =  typesTranslation[str(table.dtypes[columnTotal])]
    # fill the range of values for each column
    if (table.dtypes[columnTotal] == float) or (table.dtypes[columnTotal] == int):
        tableDescription.at[column, 'Range'] = (f'{table[columnTotal].min():.3f}', f'{table[columnTotal].max():.3f}') # https://stackoverflow.com/questions/50405021/how-to-format-float-number-in-python
    else:
        try:
            if type(eval(table.loc[0, columnTotal])) == list:
                if (type(eval(table.loc[0, columnTotal])[0]) == float) or (type(eval(table.loc[0, columnTotal])[0]) == int):
                    minimum = min(eval(table.loc[0, columnTotal]))
                    maximum = max(eval(table.loc[0, columnTotal]))
                    for L in table[columnTotal]:
                        l = eval(L)
                        if min(l) < minimum:
                            minimum = min(l)
                        if max(l) > maximum:
                            maximum = max(l)
                    tableDescription.at[column, 'Range'] = (f'{minimum:.3f}', f'{maximum:.3f}')
                elif (type(eval(table.loc[0, columnTotal])[0]) == complex):
                    for i in range(len(eval(table.loc[0, columnTotal]))):
                        c = eval(table.loc[0, columnTotal])[i]
                        if i == 0:
                            minimumComplex = c
                            maximumComplex = c
                        else:
                            norm_new = np.sqrt((c.real)**2. + (c.imag)**2.)
                            norm_min = np.sqrt((minimumComplex.real)**2. + (minimumComplex.imag)**2.)
                            norm_max = np.sqrt((maximumComplex.real)**2. + (maximumComplex.imag)**2.)
                            if norm_new < norm_min:
                                minimumComplex = c
                            if norm_new > norm_max:
                                maximumComplex = c
                    sign_min = '-' if minimumComplex.imag < 0. else '+'
                    sign_min = '-' if maximumComplex.imag < 0. else '+'
                    tableDescription.at[column, 'Range'] = (f'{minimumComplex.real:.3f} {sign_min} {np.abs(minimumComplex.imag):.3f}j', f'{maximumComplex.real:.3f} {sign_max} {np.abs(maximumComplex.imag):.3f}j')
                else:
                    tableDescription.at[column, 'Range'] = 'not applicable'
            elif type(eval(table.loc[0, columnTotal])) == tuple:
                minimumCC = eval(table.loc[0, columnTotal])[0]
                maximumCC = eval(table.loc[0, columnTotal])[0]

                minimumCCstdev = eval(table.loc[0, columnTotal])[1]
                maximumCCstdev = eval(table.loc[0, columnTotal])[1]

                for T in table[columnTotal]:
                    t = eval(T)
                    if t[0] < minimumCC:
                        minimumCC = t[0]
                    elif t[0] < minimumCC:
                        maximumCC = t[0]
                    if t[1] < minimumCCstdev:
                        minimumCCstdev = t[1]
                    elif t[1] > maximumCCstdev:
                        maximumCCstdev = t[1]
                tableDescription.at[column, 'Range'] = f'({minimumCC:.3f}, {maximumCC:.3f}) ; ({minimumCCstdev:.3f} , {maximumCCstdev:.3f})'
            else:  
                tableDescription.at[column, 'Range'] = 'not applicable'
        except (NameError, SyntaxError):
            tableDescription.at[column, 'Range'] = 'not applicable'
    # fill in the number of unique entries
    tableDescription.at[column, 'Unique entries'] = len(table[columnTotal].unique())
    tableDescription.at[column, 'Units'] = table[column].columns.get_level_values('unit')[0]

tableDescription.reset_index(inplace=True)


with pd.option_context('max_colwidth', None):   # https://stackoverflow.com/questions/67419916/pandas-df-to-latex-output-gets-truncated
    tableDescription.to_latex(f'{savepath}/Dataframe_description.tex', label='tab:dataTableDescription', caption=('This table describes the data comprised in the dataset presented here.', 'Description of the dataset.'), position='htb', index=False)   # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_latex.html
with open(r'C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data\Dataframe_description.tex', 'r') as texFile:
    tex = texFile.read()

tex = tex.replace(r'\begin{tabular}{llllll}', r'')
tex = tex.replace(r'\centering', r'')
tex = tex.replace(r'\caption[Description of the dataset.]{This table describes the data comprised in the dataset presented here.}', r'')
tex = tex.replace(r'\label{tab:dataTableDescription}', '')
tex = tex.replace(r'\begin{table}[htb]', '\\begin{landscape}\n\\begin{longtable}{lp{0.45\\textwidth}llll}')
tex = tex.replace(r'\end{table}', '\caption[Description of the dataset.]{This table describes the data comprised in the dataset presented herein.}\n\label{tab:dataTableDescription}\n\end{longtable}\n\end{landscape}')
tex = tex.replace(r'\end{tabular}', r'')
tex = tex.replace(r'\textbackslash textit', r'\textit')
tex = tex.replace('\n\n\n\\toprule', r'\toprule')
tex = tex.replace(r'\{', r'{')
tex = tex.replace(r'\}', r'}')
tex = tex.replace(r'\textasciitilde', r'~')
tex = tex.replace(r' \textbackslash cite', r'\cite')

with open(r'C:\Users\fuzha\OneDrive\Fuzhi\KIT\madap\data\Dataframe_description.tex', 'w') as texFile:
    tex = texFile.write(tex)