from __future__ import annotations

import datetime
import pathlib
import requests
import logging

from multiprocessing import current_process
from tqdm.auto import tqdm
from tqdm.contrib.concurrent import process_map

logger = logging.getLogger(__name__)


class GediAgent:
    """
    A class to interact with GEDI (Global Ecosystem Dynamics Investigation) data.

    This class provides class methods to download GEDI data based on specified
    product types, date ranges, bounding boxes, or shapefiles.

    Class Attributes:
        CONCEPT_IDS (dict): Mapping of GEDI product to their respective Concept IDs.
        DEFAULT_START_DATE (str): Default start date for temporal data filtering.
        CHUNK_SIZE (int): Size of chunks for data download, in bytes.
        API_PAGE_SIZE (int): Number of items to request per API call.
        API_PROVIDER (str): Provider name for the API.
        BASE_API_URL_JSON (str): Base URL for JSON API.
        BASE_API_URL_GRANULES (str): Base URL for granules API.

    Examples:
        >>> GediAgent.download_gedi('GEDI01_B.002', './downloads')
    """
    CONCEPT_IDS = {
        'GEDI01_B.002': 'C1908344278-LPDAAC_ECS',
        'GEDI02_A.002': 'C1908348134-LPDAAC_ECS',
        'GEDI02_B.002': 'C1908350066-LPDAAC_ECS'
    }
    DEFAULT_START_DATE = '2019-03-25'
    CHUNK_SIZE = 2 * 1024 * 1024  # 2 MB
    API_PAGE_SIZE = 2000
    API_PROVIDER = 'LPDAAC_ECS'
    BASE_API_URL_JSON = "https://cmr.earthdata.nasa.gov/search/granules.json"
    BASE_API_URL_GRANULES = "https://cmr.earthdata.nasa.gov/search/granules"

    @classmethod
    def _download_url(cls, url, download_path):
        """
        Downloads a file from a given URL to a specified path.

        Args:
            url (str): URL of the file to download.
            download_path (str): The path where the downloaded file will be saved.

        Raises:
            Exception: If there is any issue during the download.
        """
        p = current_process()
        pos = p._identity[0]
        name = f"{download_path}/{url.rsplit('/', 1)[-1]}"
        file_path = pathlib.Path(name)

        if file_path.exists():
            downloaded = file_path.stat().st_size
            resume_header = {'Range': f'bytes={downloaded}-'}
        else:
            resume_header = None
            downloaded = 0

        try:
            headers = requests.head(url, headers={'accept-encoding': ''}).headers
            file_size = int(headers['Content-Length'])

            if downloaded == file_size:
                return

            r = requests.get(url, stream=True, timeout=120, headers=resume_header)
            r.raise_for_status()

            pbar = tqdm(desc=url.rsplit('/', 1)[-1], total=file_size, unit='B',
                        unit_scale=True, unit_divisor=1024, leave=False, position=pos)

            with open(name, 'ab') as fp:
                for chunk in r.iter_content(chunk_size=cls.CHUNK_SIZE):
                    downloaded += fp.write(chunk)
                    pbar.update(len(chunk))

        except Exception as e:
            logger.error(f"Exception during download: {e}")

    @classmethod
    def _wrapper_download_url(cls, url_and_path):
        """
        Wrapper method for `_download_url` for multiprocessing.

        Args:
            url_and_path (tuple): Tuple containing the URL and the download path.

        Returns:
            None
        """
        url, download_path = url_and_path
        return cls._download_url(url, download_path)

    @classmethod
    def download_gedi(cls, product, download_path, start_date=None, end_date=None, bbox=None, shapefile=None,
                      batch_size=10):
        """
        Download GEDI data based on specified parameters. Has support for parallel and partial downloads.
        Args:
            product (str): The GEDI product type to download.
            download_path (str): The directory where downloaded files will be saved.
            start_date (str, optional): Start date for temporal filtering. Defaults to None.
            end_date (str, optional): End date for temporal filtering. Defaults to None.
            bbox (list, optional): Bounding box for spatial filtering. Defaults to None.
            shapefile (str, optional): Path to shapefile for spatial filtering. Defaults to None.
            batch_size (int, optional): Number of concurrent downloads. Defaults to 10.

        Raises:
            Exception: If there is any issue during the API request or download.
        """
        download_links = cls._get_download_links(product, start_date, end_date, bbox, shapefile)
        logger.info(f"Found {len(download_links)} {product} files for download.")
        process_map(cls._wrapper_download_url, [(url, download_path) for url in download_links], max_workers=batch_size,
                    chunksize=1, desc="Total Progress")

    @classmethod
    def _build_base_url(cls, product, start_date, end_date):
        """
        Build the base URL for the API request.

        Args:
            product (str): The GEDI product type.
            start_date (str): Start date for temporal filtering.
            end_date (str): End date for temporal filtering.

        Returns:
            tuple: The base URL and the temporal string used for filtering.
        """
        concept_id = cls.CONCEPT_IDS.get(product, "")
        start = cls._date_to_iso(start_date, cls.DEFAULT_START_DATE)
        end = cls._date_to_iso(end_date, datetime.datetime.utcnow().strftime('%Y-%m-%d'))
        temporal = f"{start},{end}"
        return f"{cls.BASE_API_URL_JSON}?provider={cls.API_PROVIDER}&page_size={cls.API_PAGE_SIZE}&concept_id={concept_id}&temporal={temporal}", temporal

    @classmethod
    def _date_to_iso(cls, date_str, default):
        """
        Convert a date string to ISO8601 format.

        Args:
            date_str (str): The date string in 'YYYY-MM-DD' format.
            default (str): The default date string in 'YYYY-MM-DD' format.

        Returns:
            str: The date in ISO8601 format.
        """
        if date_str:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            date = datetime.datetime.strptime(default, '%Y-%m-%d')
        return date.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    @classmethod
    def _get_download_links(cls, product, start_date, end_date, bbox, shapefile):
        """
        Retrieve download links from the API based on specified parameters.

        Args:
            product (str): The GEDI product type.
            start_date (str): Start date for temporal filtering.
            end_date (str): End date for temporal filtering.
            bbox (list): Bounding box for spatial filtering.
            shapefile (str): Path to shapefile for spatial filtering.

        Returns:
            list: A list of download links.

        Raises:
            Exception: If there is any issue during the API request.
        """
        pbar = tqdm(desc="Fetching links", leave=False, position=0)

        if bbox is not None and shapefile is not None:
            logger.warning("Ignoring shapefile since a bounding box was also supplied.")

        base_url, temporal = cls._build_base_url(product, start_date, end_date)
        url = base_url
        response = None
        page = 1
        if bbox:
            bounding_box = ','.join([str(pnt) for pnt in bbox])
            url = f"{base_url}&bounding_box={bounding_box}"
        elif shapefile:
            files = {'shapefile': (shapefile.split('/')[-1], open(shapefile, 'rb'), 'application/geo+json')}
            url = cls.BASE_API_URL_GRANULES
            values = {
                'provider': cls.API_PROVIDER,
                'page_size': cls.API_PAGE_SIZE,
                'concept_id': cls.CONCEPT_IDS[product],
                'temporal': temporal
            }
            headers = {'Accept': 'application/json'}
            response = requests.post(url, files=files, data=values, headers=headers)

        if response is None:
            response = requests.get(f"{url}&pageNum={page}")

        if response.status_code != 200:
            pbar.close()
            raise Exception(
                f"There was an error connecting to the CMR API. Exception: {response.text}"
            )
        entries = response.json()['feed']['entry']

        download_links = [entry['links'][0]['href'] for entry in entries if
                          entry['links'][0]['href'].split('.')[-1] == 'h5']
        pbar.update(1)

        try:
            while len(entries) % 2000 == 0:
                page += 1
                response = requests.get(f"{url}&pageNum={page}")
                if response.status_code != 200:
                    raise Exception(
                        f"There was an error connecting to the CMR API. Exception: {response.text}"
                    )
                entries = response.json()['feed']['entry']
                for entry in entries:
                    if entry['links'][0]['href'].split('.')[-1] != 'h5':
                        continue
                    download_links.append(entry['links'][0]['href'])
                pbar.update(1)
        except Exception as e:
            logger.error(f"There was an error getting links. Exception: {e}")
            raise

        pbar.close()
        return download_links
