import urllib.request
from pathlib import Path

root = Path(r"c:\Users\pooja\OneDrive\Desktop\Ai healthcare")
root.mkdir(parents=True, exist_ok=True)
for folder in ['datasets']:
    (root / folder).mkdir(parents=True, exist_ok=True)

urls = {
    'diabetes': 'https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv',
    'heart': 'https://raw.githubusercontent.com/rahul-1-nair/Heart-Disease-Prediction-dataset/master/heart.csv',
    'kidney': 'https://raw.githubusercontent.com/ishandutta2007/Chronic-Kidney-Disease-Dataset/master/kidney_disease.csv'
}

for name, url in urls.items():
    local_path = root / 'datasets' / f'{name}.csv'
    print(f'Downloading {name} dataset to {local_path}')
    try:
        urllib.request.urlretrieve(url, local_path)
        print('Downloaded', local_path)
    except Exception as e:
        print('Failed to download', name, e)
