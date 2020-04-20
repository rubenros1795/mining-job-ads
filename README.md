# Mining Wages in Nineteenth-Century Job Advertisements

Code and resources for the paper "Mining Wages in Nineteenth-Century Job Advertisements: The Application of Language Resources and Language Technology to study Economic and Social Inequality". Submitted to the workshop "LR4SSHOC: LREC2020 workshop about Language Resources for the SSH Cloud"

This repository contains scripts for extracting information on wages in nineteenth-century job advertisements, printed in digitized historical newspapers. The newspapers are extraced by using the [National Library API](https://www.kb.nl/bronnen-zoekwijzers/dataservices-en-apis). Newspapers printed before 1876 are free of copyrights. Mining newspapers printed after 1876 requires an API-key.

The scripts in `/code` apply a rule-based classifier to a `.csv` file containing the extracted advertisements. The .csv file requires the following format:

| id            | ocr           | date          |
| ------------- | ------------- | ------------- |
| ddd:011101316:mpeg21:a0003  | Algemeen Kantoor van EXPEDITIE L. IV. H. A. CHATELDT. Dagelijksche ...  | 1869/01/13 |

The classifier identifies qualitative ("high wage!") and quantitative ("wage of f 50,-") wage indicators in advertisements. In light of lacking article segmentation a list of occupations is used to create a subset of advertisements that are likely to advertise jobs. A window of 12 words left and 40 words right of the occupation title is extracted and considered by the classifier.

## Usage

Use `pip requirements.txt` to install the necessary modules. Edit the paths to `/resources` and `/data` in the `classifier.py` script. The script exports the classified job advertisements in `[input-csv-name]_processed.csv` files. The list with occupation titles is drawn from the [HISCO dataverse](https://datasets.iisg.amsterdam/dataverse/HISCO). When using the HISCO data, cite: 

Mandemakers, K., Mourits, R., and Muurling, S. (2019). HSN HISCO Release 2018/01, December. Publisher: IISH Data Collection.
