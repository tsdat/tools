# Excel to Yaml Instructions

The goal of this tool is to simplify the process of creating dataset
configuration files for tsdat. There are two parts to this tool: an input
excel file and a jupyter notebook to run the conversion code. The excel 
file contains the user-provided dataset metadata in a simplified format, and the notebook takes the information provided in the excel file and 
reorganizes it into yaml-format, tsdat configuration files. These configuration files can then be added to a pipeline generated by the 
[pipeline-template](https://github.com/tsdat/pipeline-template).

## Excel File Description
The provided excel file template is titled "excel to yaml template.xlsx"
and contains 3 sheets labeled "Metadata", "Independent Variables" and 
"Dependent Variables". Each sheet contains a table listing information 
for different parts of what will be the finalized dataset. 

 - The "Metadata" sheet includes the global "attributes" (another word 
 for metadata) for the dataset, typically describing the 
 what-when-where-how" of the collected input data. 
 - The other two sheets break down the input data into independent and 
 dependent variables. 
    - Variables listed on the "Independent Variables" sheet will become
     the "dimensions" or "coordinates" of the dataset, like time, 
     latitude, or longitude.
    - Variables listed under "Dependent Variables" are the primary 
    measurements contained in the input datafile. 

Information in the "Metadata" sheet exists in key-item pairs, where 
elements in the top row are the keys and the bottom row are the 
corresponding items. Additional key-item pairs can be appended to 
additional columns in this sheet.

Information in the other two sheets is organized by variable. Each 
variable gets assigned a name, units, datatype, dimensions, and 
additional metadata. These inputs are described in tables below:

### Independent Variable Sheet Details
|Key              |Definition                                       |
|---              | ---                                             |
|New Name         |New variable name                                |
|Original Name    |Name of variable in raw input file               |
|Standardized Unit|New variable unit                                |
|Original Unit    |Variable unit in raw input file                  |
|Timezone         |Timezone identifier, specifically for "time" variables, from [TZ database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)      |
|Datatype         |Variable datatype (e.g. "float32")               |
|Long Name        |"Human readable" version of variable name        |
|Standard Name    |Name of variable from [CF conventions lookup table](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html)|

Note: A [list of timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) is available on wikipedia, under the 
column labeled "TZ database name".

### Dependent Variable Sheet Details
|Key              |Definition                                       |
|---              | ---                                             |
|New Name         |New variable name                                |
|Original Name    |Name of variable in raw input file               |
|Standardized Unit|New variable unit                                |
|Original Unit    |Variable unit in raw input file                  |
|Datatype         |Variable datatype (e.g. "float32")               |
|Dimensions       |Independent variable(s) corresponding to the variable, separated by a comma, if multiple  |
|Long Name        |"Human readable" version of variable name        |
|Standard Name    |Name of variable from [CF conventions lookup table](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html)|
|Description      |Optional, additional information for the variable. Good to use if a standard name isn't available |
|Valid Minimum Value |Lower range limit expected for a variable, for quality control|
|Valid Maximum Value |Upper range limit expected for a variable, for quality control|
|<new_qc_parameter>  |                                                 |
|<new_qc_parameter>  |                                                 |