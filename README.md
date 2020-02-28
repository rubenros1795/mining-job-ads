## Mining Job Advertisements from Historical Newspapers

This repository contains scripts for extracting information on wages in nineteenth-century job advertisements, printed in digitized historical newspapers. The newspapers are extraced by using the [National Library API](https://www.kb.nl/bronnen-zoekwijzers/dataservices-en-apis). Newspapers printed before 1876 are free of copyrights. Mining newspapers printed after 1876 requires an API-key.

The scripts in `/code` apply a rule-based classifier to a `.csv` file containing the extracted advertisements. The classifier identifies qualitative ("high wage!") and quantitative ("wage of f 50,-") wage indicators in advertisements. In light of lacking article segmentation a list of occupations is used to create a subset of advertisements that are likely to advertise jobs. A window of 12 words left and 40 words right of the occupation title is extracted and considered.

