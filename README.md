# prostate-reproducibility
Evaluate the reproducibility of MR cytometry mappings across protocols, and quantify the variations in prostate imaging between OGSE frequencies of 17/33Hz and 25/50Hz.

extract_radiomics.py implements the extraction of radiomics features from metric (ADC and IMPULSED-derived) mappings.

## Data Preparation
for each patient case contains 

ADC

|--P14

|----P14_1.nii
  
|----P14_2.nii
  
|----P14_PGSE.nii
  
|----P14_mask.nii
  
where suffix 1 and 2 present OGSE with 17Hz/33Hz or 25Hz/50Hz respectively.

micro

|--P14

|----P14_1.nii
  
|----P14_2.nii
  
|----P14_3.nii
  
|----P14_4.nii
  
|----P14_mask.nii
  
where suffix 1 to 4 present cell diameter, vin, cellularity and Dex respectively.
