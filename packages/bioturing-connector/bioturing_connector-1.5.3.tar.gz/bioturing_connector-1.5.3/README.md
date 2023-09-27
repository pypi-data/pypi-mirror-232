## 1. Installation:
```
  pip install bioturing_connector --index-url=https://pypi.bioturing.com

  # Username: bioturing
  # Password: code@bioturing.com
```

## 2. Usage:
**The package only allows data submission via Amazon S3 Bucket. Please configure your S3 Bucket credentials in the `Settings` page.**
### 2.1. Test the connection:
```
# example.py

from bioturing_connector.connector import BBrowserXConnector

connector = BBrowserXConnector(
  host="https://yourcompany/t2d_index_tool/,
  token="<input your token here>"
)

connector.test_connection()
```

Example output:

```
Connecting to host at https://yourcompany/t2d_index_tool/api/v1/test_connection
Connection successful
```

### 2.2. Get user groups available for your token:
```
# example.py

from bioturing_connector.connector import BBrowserXConnector

connector = BBrowserXConnector(
  host="https://yourcompany/t2d_index_tool/,
  token="<input your token here>"
)

user_groups = connector.get_user_groups()
print(user_groups)
```

Example output:

```
[{'id': 'all_members', 'name': 'All members'}, {'id': 'personal', 'name': 'Personal workspace'}]
```

### 2.3. Submit h5ad (scanpy object):
```
# example.py
from bioturing_connector.connector import BBrowserXConnector
from bioturing_connector.typing import InputMatrixType
from bioturing_connector.typing import Species

connector = BBrowserXConnector(
  host="https://yourcompany/t2d_index_tool/,
  token="<input your token here>"
)

# Call this function first to get available groups and their id.
user_groups = connector.get_user_groups()
# Example: user_groups is now [{'id': 'all_members', 'name': 'All members'}, {'id': 'personal', 'name': 'Personal workspace'}]


# Submitting the scanpy object:
connector.submit_h5ad(
  group_id='personal',
  study_s3_keys=['GSE128223.h5ad'],
  study_id='GSE128223',
  name='This is my first study',
  authors=['Huy Nguyen'],
  species=Species.HUMAN.value,
  input_matrix_type=InputMatrixType.RAW.value
)

# Example output:
> [2022-10-10 01:03] Waiting in queue
> [2022-10-10 01:03] Downloading GSE128223.h5ad from s3: 262.1 KB / 432.8 MB
> [2022-10-10 01:03] File downloaded
> [2022-10-10 01:03] Reading batch: GSE128223.h5ad
> [2022-10-10 01:03] Preprocessing expression matrix: 19121 cells x 63813 genes
> [2022-10-10 01:03] Filtered: 19121 cells remain
> [2022-10-10 01:03] Start processing study
> [2022-10-10 01:03] Normalizing expression matrix
> [2022-10-10 01:03] Running PCA
> [2022-10-10 01:03] Running kNN
> [2022-10-10 01:03] Running spectral embedding
> [2022-10-10 01:03] Running venice binarizer
> [2022-10-10 01:04] Running t-SNE
> [2022-10-10 01:04] Study was successfully submitted
> [2022-10-10 01:04] DONE !!!
> Study submitted successfully!
```
Available parameters for `submit_h5ad` function:
```
group_id: str
  ID of the group to submit the data to.

study_s3_keys: List[str]
  List of the s3 key of the studies.

study_id: str, default=None
  Study ID, if no value is specified, use a random uuidv4 string

name: str, default='TBD'
  Name of the study.

authors: List[str], default=[]
  Authors of the study.

abstract: str, default=''
  Abstract of the study.

species: str, default='human'
  Species of the study. Can be: **bioturing_connector.typing.Species.HUMAN.value** or **bioturing_connector.typing.Species.MOUSE.value** or **bioturing_connector.typing.Species.NON_HUMAN_PRIMATE.value**

input_matrix_type: str, default='raw'
  If the value of this input is **bioturing_connector.typing.InputMatrixType.NORMALIZED.value**,
  then the software will
  use slot 'X' from the scanpy object and does not apply normalization.
  If the value of this input is **bioturing_connector.typing.InputMatrixType.RAW.value**,then the software will
  use slot 'raw.X' from thescanpy object and apply log-normalization.

min_counts: int, default=None
  Minimum number of counts required
  for a cell to pass filtering.

min_genes: int, default=None
  Minimum number of genes expressed required
  for a cell to pass filtering.

max_counts: int, default=None
  Maximum number of counts required
  for a cell to pass filtering.

max_genes: int, default=None
  Maximum number of genes expressed required
  for a cell to pass filtering.

mt_percentage: Union[int, float], default=None
  Maximum number of mitochondria genes percentage
  required for a cell to pass filtering. Ranging from 0 to 100
```
