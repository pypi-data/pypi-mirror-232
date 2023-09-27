"""Python package for submitting/getting data from BBrowserX"""

import pandas as pd
from pathlib import Path

from urllib.parse import urljoin
from typing import List
from typing import Union

from .common import get_uuid
from .common import decode_base64_array

from .common.https_agent import HttpsAgent
from .common import common
from .typing import Species
from .typing import StudyType
from .typing import ChunkSize
from .typing import InputMatrixType
from .typing import UNIT_RAW

class BBrowserXConnector:
  """Create a connector object to submit/get data from BBrowserX
  """
  def __init__(self, host: str, token: str, ssl: bool = True):
    """
      Args:
        host:
          The URL of the BBrowserX server, only support HTTPS connection
          Example: https://bbrowserx.bioturing.com
        token:
          The API token to verify authority. Generated in-app.
    """
    self.__host = host
    self.__token = token
    self.__https_agent = HttpsAgent(self.__token, ssl)


  def _submit_study(
    self,
    group_id: str,
    study_id: str = None,
    name: str = 'TBD',
    authors: List[str] = [],
    abstract: str = '',
    species: str = Species.HUMAN.value,
    input_matrix_type: str = InputMatrixType.NORMALIZED.value,
    study_type: int = StudyType.H5AD.value,
    min_counts: int = None,
    min_genes: int = None,
    max_counts: int = None,
    max_genes: int = None,
    mt_percentage: Union[int, float] = None,
    skip_dimred: bool = False,
  ):
    if study_id is None:
      study_id = get_uuid()

    if min_counts is None:
      min_counts = 0

    if min_genes is None:
      min_genes = 0

    if max_counts is None:
      max_counts = 1e9

    if max_genes is None:
      max_genes = 1e9

    if mt_percentage is None:
      mt_percentage = 100

    study_info = {
      'study_hash_id': study_id,
      'name': name,
      'authors': authors if authors else [],
      'abstract': abstract
    }

    return {
      'species': species,
      'group_id': group_id,
      'filter_params': {
        'min_counts': min_counts,
        'min_genes': min_genes,
        'max_counts': max_counts,
        'max_genes': max_genes,
        'mt_percentage': mt_percentage / 100
      },
      'study_type': study_type,
      'normalize': input_matrix_type == InputMatrixType.RAW.value,
      'subsample': -1,
      'skip_dimred': skip_dimred,
      'study_info': study_info,
    }


  def test_connection(self):
    """Test the connection with the host
    """
    url = urljoin(self.__host, 'api/v1/test_connection')

    print(f'Connecting to host at {url}')
    res = self.__https_agent.post(url=url)
    if res and 'status' in res and res['status'] == 200:
      print('Connection successful')
    else:
      print('Connection failed')


  def get_user_groups(self):
    """
      Get all the data sharing groups available for the current token
      ------------------
      Returns:
        [{
          'group_id': str (uuid),
          'group_name': str
        }, ...]
    """
    url = urljoin(self.__host, 'api/v1/get_user_groups')

    res = self.__https_agent.post(url=url)
    if res and 'status' in res and res['status'] == 200:
      return res['data']
    raise Exception('''Something went wrong, please contact support@bioturing.com''')


  def submit_study_from_s3(
    self,
    group_id: str,
    batch_info: List[dict] = [],
    study_id: str = None,
    name: str = 'TBD',
    authors: List[str] = [],
    abstract: str = '',
    species: str = Species.HUMAN.value,
    input_matrix_type: str = InputMatrixType.NORMALIZED.value,
    study_type: int = StudyType.H5AD.value,
    min_counts: int = None,
    min_genes: int = None,
    max_counts: int = None,
    max_genes: int = None,
    mt_percentage: Union[int, float] = None,
    skip_dimred: bool = False
  ):
    """
      Submit one or multiple datasets from s3 bucket to BBrowserX.

      Args:
      ------
        group_id: str
              ID of the group to submit the data to.
        batch_info: List[dict]
              File path and batch name information, the path should exclude bucket path!
              Example:
                For h5ad format:
                  [{
                    'matrix': 's3_path/GSE128223_1.h5ad'
                  }, {...}]
                For mtx format:
                  [{
                    'matrix': 's3_path/data_1/matrix.mtx',
                    'features': 's3_path/data_1/features.tsv',
                    'barcodes': 's3_path/data_1/barcodes.tsv',
                  }, {...}]
                For tiledb format:
                  [{
                    'folder': 's3_path/GSE128223_1'
                  }, {...}]
        study_id: str
              If no value is provided, default id will be a random uuidv4 string
        name: str
              Name of the study.
        authors: List[str]
              Authors of the study.
        abstract: str
              Abstract of the study.
        species: str
              Species of the study.
              Support:
                    Species.HUMAN.value
                    Species.MOUSE.value
                    Species.NON_HUMAN_PRIMATE.value
                    Species.OTHERS.value
        skip_dimred: Bool
              Skip BioTuring pipeline if set to True (only applicable when input is a scanpy/seurat object).
        input_matrix_type: str
              Is the input matrix already normalized or not?
              Support:
                    InputMatrixType.NORMALIZED.value (will skip BioTuring normalization, h5ad: use adata.X)
                    InputMatrixType.RAW.value (apply BioTuring normalization, h5ad: use adata.raw.X)
        study_type: int
              Format of dataset
              Support:
                    StudyType.BBROWSER.value
                    StudyType.H5_10X.value
                    StudyType.H5AD.value
                    StudyType.MTX_10X.value
                    StudyType.BCS.value
                    StudyType.RDS.value
                    StudyType.TSV.value
        min_counts: int. Default 0
              Minimum number of counts required for a cell to pass filtering.
        min_genes: int. Default 0
              Minimum number of genes expressed required for a cell to pass filtering.
        max_counts: int. Default inf
              Maximum number of counts required for a cell to pass filtering.
        max_genes: int. Default inf
              Maximum number of genes expressed required for a cell to pass filtering.
        mt_percentage: int. Default 100
              Maximum number of mitochondria genes percentage required for a cell to pass filtering.
              Ranging from 0 to 100
    """
    data = self._submit_study(
      group_id,
      study_id,
      name,
      authors,
      abstract,
      species,
      input_matrix_type,
      study_type,
      min_counts,
      min_genes,
      max_counts,
      max_genes,
      mt_percentage,
      skip_dimred,
    )

    if study_type == StudyType.MTX_10X.value:
      for i, o in enumerate(batch_info):
        name = o['matrix'].split('/')
        if len(name) == 1:
          o['name'] = f'Batch {i + 1}'
        else:
          o['name'] = name[-2]
    elif study_type == StudyType.TILE_DB.value:
      for i, o in enumerate(batch_info):
        o['name'] = o['folder'].split('/')[-1]
    else:
      for i, o in enumerate(batch_info):
        o['name'] = o['matrix'].split('/')[-1]

    data['batch_info'] = {f'Batch_{i}': o for i, o in enumerate(batch_info)}

    submission_status = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/submit_study_from_s3'),
      body=data
    )

    task_id = common.parse_submission_status(submission_status)
    if task_id is None:
      return False

    return common.get_submission_log(
      group_id=group_id, task_id=task_id, https_agent=self.__https_agent, host=self.__host
    )


  def submit_study_from_local(
    self,
    group_id: str,
    batch_info: object,
    study_id: str = None,
    name: str = 'TBD',
    authors: List[str] = [],
    abstract: str = '',
    species: str = Species.HUMAN.value,
    input_matrix_type: str = InputMatrixType.NORMALIZED.value,
    study_type: int = StudyType.H5AD.value,
    min_counts: int = None,
    min_genes: int = None,
    max_counts: int = None,
    max_genes: int = None,
    mt_percentage: Union[int, float] = None,
    skip_dimred: bool = False,
    chunk_size: int = ChunkSize.CHUNK_100_MB.value
  ):
    """Submit one or multiple datasets from local / server.

      Args:
      -----
        group_id: str
              ID of the group to submit the data to.
        batch_info: List[dict]
              File path and batch name information.
              Example:
                For h5ad format:
                  [{
                    'matrix': 'local_path/GSE128223_1.h5ad'
                  }, {...}]
                For mtx format:
                  [{
                    'name': 'data_1',
                    'matrix': 'local_path/data_1/matrix.mtx',
                    'features': 'local_path/data_1/features.tsv',
                    'barcodes': 'local_path/data_1/barcodes.tsv',
                  }, {...}]
        study_id: str
              If no value is provided, default id will be a random uuidv4 string
        name: str
              Name of the study.
        authors: List[str]
              Authors of the study.
        abstract: str
              Abstract of the study.
        species: str
              Species of the study.
              Support:
                    Species.HUMAN.value
                    Species.MOUSE.value
                    Species.NON_HUMAN_PRIMATE.value
                    Species.OTHERS.value
        skip_dimred: bool
              Skip BioTuring pipline if set to True (only appliable when input is a scanpy/seurat object).
        input_matrix_type: str
              Is the input matrix already normalized or not?
              Support:
                  InputMatrixType.NORMALIZED.value (will skip BioTuring normalization, h5ad: use adata.X)
                  InputMatrixType.RAW.value (apply BioTuring normalization, h5ad: use adata.raw.X)
        study_type: int
              Format of dataset
              Support:
                    StudyType.BBROWSER.value
                    StudyType.H5_10X.value
                    StudyType.H5AD.value
                    StudyType.MTX_10X.value
                    StudyType.BCS.value
                    StudyType.RDS.value
                    StudyType.TSV.value
        min_counts: int. Default 0
              Minimum number of counts required for a cell to pass filtering.
        min_genes: int. Default 0
              Minimum number of genes expressed required for a cell to pass filtering.
        max_counts: int. Default inf
              Maximum number of counts required for a cell to pass filtering.
        max_genes: int. Default inf
              Maximum number of genes expressed required for a cell to pass filtering.
        mt_percentage: int. Default 100
              Maximum number of mitochondria genes percentage required for a cell to pass filtering.
              Ranging from 0 to 100
        chunk_size: int. Default: ChunkSize.CHUNK_100_MB.value
              size of each separated chunk for uploading
              Support:
                    ChunkSize.CHUNK_5_MB.value
                    ChunkSize.CHUNK_100_MB.value
                    ChunkSize.CHUNK_500_MB.value
                    ChunkSize.CHUNK_1_GB.value
    """
    if study_type == StudyType.TILE_DB.value:
      return 'Tile_db submission is only supported through s3 or shared folder'

    if chunk_size not in [e.value for e in ChunkSize]:
      return 'Only support: \nChunkSize.CHUNK_5_MB.value, \nChunkSize.CHUNK_100_MB.value, \nChunkSize.CHUNK_500_MB.value, \nChunkSize.CHUNK_1_GB.value'

    file_names = []
    files = []
    if study_type == StudyType.MTX_10X.value:
      for o in batch_info:
        file_names.extend([
          f'{o["name"]}matrix.mtx{".gz" if ".gz" in o["matrix"] else ""}',
          f'{o["name"]}features.tsv{".gz" if ".gz" in o["features"] else ""}',
          f'{o["name"]}barcodes.csv{".gz" if ".gz" in o["barcodes"] else ""}'
        ])
        files.extend([
          Path(o['matrix']),
          Path(o['features']),
          Path(o['barcodes'])
        ])
    else:
      for o in batch_info:
        p = Path(o['matrix'])
        o['name'] = p.name
        file_names.append(p.name)
        files.append(p)


    output_dir = common.upload_chunk(
      file_names,
      files,
      self.__token,
      self.__host,
      chunk_size
    )
    data = self._submit_study(
      group_id,
      study_id,
      name,
      authors,
      abstract,
      species,
      input_matrix_type,
      study_type,
      min_counts,
      min_genes,
      max_counts,
      max_genes,
      mt_percentage,
      skip_dimred,
    )
    data['study_path'] = output_dir
    data['batch_info'] = [o['name'] for o in batch_info]

    submission_status = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/submit_study_from_local'),
      body=data
    )

    task_id = common.parse_submission_status(submission_status)
    if task_id is None:
      return False

    return common.get_submission_log(
      group_id=group_id,
      task_id=task_id,
      https_agent=self.__https_agent,
      host=self.__host
    )


  def query_genes(
    self,
    species: str,
    study_id: str,
    gene_names: List[str],
    unit: str = UNIT_RAW
  ):
    """
      Query genes expression in study.
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study hash ID
        gene_names : list of str
          Querying gene names. If gene_names=[], full matrix will be returned
        unit: str
          Expression unit, UNIT_LOGNORM or UNIT_RAW. Default is UNIT_RAW
      --------------
      Returns
        expression_matrix : csc_matrix
          Expression matrix, shape=(n_cells, n_genes)
    """
    data = {
      'species': species,
      'study_id': study_id,
      'gene_names': gene_names,
      'unit': unit
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/study/query_genes'),
      body=data
    )
    return common.parse_query_genes_result(result)


  def get_metadata(
    self,
    species: str,
    study_id: str
  ):
    """
      Get full metadata of a study.
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study hash ID
      -------------
      Returns
        Metadata: pd.DataFrame
    """
    data = {
      'species': species,
      'study_id': study_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/study/get_metadata'),
      body=data
    )
    common.check_result_status(result)
    metadata_dict = result['data']
    metadata_df = pd.DataFrame(metadata_dict)
    return metadata_df


  def get_barcodes(
    self,
    species: str,
    study_id: str
  ):
    """
      Get barcodes of a study.
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study hash ID
      -------------
      Returns
        Barcodes: List[str]
    """
    data = {
      'species': species,
      'study_id': study_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/study/get_barcodes'),
      body=data
    )
    common.check_result_status(result)
    return result['data']


  def get_features(
    self,
    species: str,
    study_id: str
  ):
    """
      Get features of a study.
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study hash ID
      -------------
      Returns
        Features: List[str]
    """
    data = {
      'species': species,
      'study_id': study_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/study/get_features'),
      body=data
    )
    common.check_result_status(result)
    return result['data']


  def get_all_studies_info_in_group(
    self,
    species: str,
    group_id: str
  ):
    """
      Get info of all studies within group.
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        group_id: str,
          Group hash id (uuid)
      -------------
      Returns
        [
          {
            'uuid': str (uuid),
            'study_hash_id': str (GSE******),
            'study_title': str,
            'created_by': str
          }, ...
        ]
    """
    data = {
      'species': species,
      'group_id': group_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/get_all_studies_info_in_group'),
      body=data
    )
    common.check_result_status(result)
    return result['data']


  def list_all_custom_embeddings(
    self,
    species: str,
    study_id: str
  ):
    """
      List out all custom embeddings in a study
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study id (uuid)
      -------------
      Returns
        [
          {
          'embedding_id': str,
          'embedding_name': str
          }, ...
        ]
    """
    data = {
      'species': species,
      'study_id': study_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/list_all_custom_embeddings'),
      body=data
    )
    common.check_result_status(result)
    return result['data']


  def retrieve_custom_embedding(
    self,
    species: str,
    study_id: str,
    embedding_id: str
  ):
    """
      Retrive custom embedding array in the study
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study id (uuid)
        embedding_id: str,
          Embedding id (uuid)
      -------------
      Returns
        embedding_arr: np.ndarray
    """
    data = {
      'species': species,
      'study_id': study_id,
      'embedding_id': embedding_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/retrieve_custom_embedding'),
      body=data
    )
    common.check_result_status(result)
    coord_arr = result['data']['coord_arr']
    coord_shape = result['data']['coord_shape']
    return decode_base64_array(coord_arr, 'float32', coord_shape)


  def submit_metadata_from_dataframe(
    self,
    species: str,
    study_id: str,
    group_id: str,
    df: pd.DataFrame
  ):
    """
      Submit metadata dataframe directly to platform
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study id (uuid)
        group_id: str,
          ID of the group containing study id
        df: pandas DataFrame,
          Barcodes must be in df.index!!!!
      -------------
      Returns
        'Successful' or Error log
    """
    metadata_dct = common.dataframe2dictionary(df)
    data = {
      'species': species,
      'study_id': study_id,
      'group_id': group_id,
      'metadata_dct': metadata_dct
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/submit_metadata_dataframe'),
      body=data
    )
    common.check_result_status(result)
    return 'Successful'


  def submit_metadata_from_local(
    self,
    species: str,
    study_id: str,
    group_id: str,
    file_path: str
  ):
    """
      Submit metadata to platform with local path
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study id (uuid)
        group_id: str,
          ID of the group containing study id
        file_path: local path leading to metadata file,
          Barcodes must be in the fist column
          File suffix must be in .tsv/.csv
      -------------
      Returns
        'Successful' or Error log
    """
    df = common.read_csv(file_path, index_col=0)
    return self.submit_metadata_from_dataframe(
      species,
      study_id,
      group_id,
      df
    )


  def submit_metadata_from_s3(
    self,
    species: str,
    study_id: str,
    group_id: str,
    file_path: str
  ):
    """
      Submit metadata to platform with s3 path
      -------------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        study_id: str,
          Study id (uuid)
        group_id: str,
          ID of the group containing study id
        file_path: path in s3 bucket leading to metadata file,
          Barcodes must be in the fist column
          File suffix must be in .tsv/.csv
          File_path DOES NOT contain s3_bucket path configured in the platform
              E.g. realpath: 's3://bucket/folder/metadata.tsv'
                  inputpath: 'folder/metadata.tsv'
      -------------
      Returns
        'Successful' or Error log
    """
    data = {
      'species': species,
      'study_id': study_id,
      'group_id': group_id,
      'file_path': file_path
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/submit_metadata_s3'),
      body=data
    )
    common.check_result_status(result)
    return 'Successful'


  def get_ontologies_tree(
    self,
    species,
    group_id,
  ):
    """
      Get standardized ontologies tree
      ------
      Args:
        species: str,
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        group_id
          ID of the group.
    """
    data = {
      'species': species,
      'group_id': group_id
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/get_ontologies'),
      body=data
    )
    common.check_result_status(result)
    return result['data']


  def assign_standardized_meta(
    self,
    species,
    group_id,
    study_id,
    metadata_field,
    metadata_value,
    root_name,
    leaf_name,
  ):
    """
      Assign metadata value to standardized term on ontologies tree
      -------
      Args:
        species: str
          Species of the study.
          Support:  Species.HUMAN.value
                    Species.MOUSE.value
                    Species.PRIMATE.value
                    Species.OTHERS.value
        group_id: str
          ID of the group to submit the data to.
        study_id: str
          ID of the study (uuid)
        metadata_field: str
          ~ column name of meta dataframe in platform (eg: author's tissue)
        metadata_value: str
          ~ metadata value within the metadata field (eg: normal lung)
        root_name: str
          name of root in btr ontologies tree (eg: tissue)
        leaf_name: str
          name of leaf in btr ontologies tree (eg: lung)
    """
    ontologies_tree = self.get_ontologies_tree(species, group_id)
    root_id, leaf_id = common.parse_root_leaf_name(
      ontologies_tree,
      root_name,
      leaf_name
    )
    data = {
      'species': species,
      'group_id': group_id,
      'study_id': study_id,
      'group': metadata_field,
      'name': metadata_value,
      'root_id': root_id,
      'leaf_id': leaf_id,
    }
    result = self.__https_agent.post(
      url=urljoin(self.__host, 'api/v1/study/assign_standardized_term'),
      body=data
    )
    common.check_result_status(result)
    return 'Successul'

