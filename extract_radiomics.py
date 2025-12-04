import os
import logging
import pandas as pd
from radiomics import featureextractor, logger
import SimpleITK as sitk

# log settings
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='../log/IMPLUSED_50hz_log.txt', mode='w')
formatter = logging.Formatter("%(levelname)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def extract_features(base_path, output_file, is_adc=False):
    """
    batch extract radiomic features from nii files and save to Excel file
    
    params:
        base_path: base path (parent directory of ADC or micro folder)
        output_file: output Excel file name
        is_adc: is ADC file (True/False)
    """
    # parameter settings
    settings = {
        'binWidth': 0.1,
        'interpolator': sitk.sitkBSpline,
        # 'normalize': True
    }
    
    # initialize feature extractor
    extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
    extractor.disableAllFeatures()
    
    # enable feature classes
    extractor.enableFeatureClassByName('firstorder')
    extractor.enableFeatureClassByName('shape')
    extractor.enableFeatureClassByName('glszm')
    extractor.enableFeatureClassByName('glrlm')
    extractor.enableFeatureClassByName('ngtdm')
    extractor.enableFeatureClassByName('gldm')
    extractor.enableFeaturesByName(glcm=['Autocorrelation', 'ClusterProminence', 'ClusterShade', 'ClusterTendency', 'Contrast', 'Correlation','DifferenceAverage','DifferenceEntropy','DifferenceVariance', 'JointEnergy', 'JointEntropy', 'Imc1', 'Imc2', 'Idm','MCC','Idmn','Id','Idn','InverseVariance','MaximumProbability','JointAverage','SumEntropy','SumSquares'])

    # enable image types
    extractor.enableImageTypes(Original={}, LoG={"sigma" : [3.0]}, Gradient={})
    
    # save all features
    all_features = []
    
    # patient loop
    for patient_id in sorted(os.listdir(base_path)):
        if not patient_id.startswith('P'):
            continue
            
        patient_path = os.path.join(base_path, patient_id)
        
        # read mask file
        mask_path = os.path.join(patient_path, f'{patient_id}_mask.nii')
        if not os.path.exists(mask_path):
            print(f"warning: {mask_path} does not exist, skip this patient")
            continue

        if is_adc:
            # ADC: 1:25Hz/17Hz, 2:50Hz/33Hz, PGSE
            image_files = [
                f'{patient_id}_1.nii',
                f'{patient_id}_2.nii',
                f'{patient_id}_PGSE.nii'
            ]
        else:
            # IMPULSED-derived parameters: 1:d 2:vin 3:cellularity 4:Dex
            image_files = [
                f'{patient_id}_1.nii',
                f'{patient_id}_2.nii',
                f'{patient_id}_3.nii',
                f'{patient_id}_4.nii'
            ]

        patient_features = {} 

        for img_file in image_files:
            image_path = os.path.join(patient_path, img_file)
            if not os.path.exists(image_path):
                print(f"warning: {image_path} does not exist, skip")
                continue
            try:
                # extract features
                feature_vector = extractor.execute(image_path, mask_path)
                
                # add patient id
                feature_vector['Patient'] = patient_id
                
                # extract suffix (25hz, 50hz, PGSE)
                suffix = img_file.split('_')[-1].split('.')[0]
                
                # rename features
                items = list(feature_vector.items())
                for i, (key, value) in enumerate(items[22:], 23):  # start from 23rd feature skip version description
                    if key not in ['Patient']:
                        if key.startswith('original_shape_'):
                            # save shape features only once
                            if suffix == '25hz'or suffix == '1':
                                patient_features[key] = value  
                        else:
                            new_key = f"{key}_{suffix}"
                            patient_features[new_key] = value
                    else:
                        patient_features[key] = value 
            except Exception as e:
                print(f"failed {patient_id}/{img_file}: {str(e)}")    

        all_features.append(patient_features)   
        print(f"successfully extract features: {patient_id}")
                
    if all_features:
        df = pd.DataFrame(all_features)
        
        # sort by patient id
        df['Patient_num'] = df['Patient'].str.extract('(\d+)').astype(int)
        df = df.sort_values('Patient_num').drop('Patient_num', axis=1)

        cols = ['Patient'] + [col for col in df.columns if col not in ['Patient']]
        df = df[cols]

        df.to_excel(output_file, index=False)
        print(f"save features to {output_file}")
    else:
        print("warning: no features extracted")


if __name__ == '__main__':
    save_dir='../radiomics_feature/'
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    adc_path = '../nii/50Hz/ADC'
    micro_path = '../nii/50Hz/micro'
    extract_features(adc_path, save_dir+'/ADC_50Hz.xlsx', is_adc=True)
    extract_features(micro_path, save_dir+'/micro_50Hz.xlsx', is_adc=False)



    