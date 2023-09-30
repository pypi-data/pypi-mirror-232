from dataclasses import dataclass, field
from typing import Optional
from tesseract_olap import DataRequest, DataRequestParams

import economic_complexity
import pandas as pd

from .rca import RcaParameters


@dataclass
class PEIIParameters:
    rca_params: RcaParameters
    cube_emissions: str
    measure_emissions: str
    location_emissions: str
    cutoff: float
    rank: bool = field(default=False)
    sort_ascending: Optional[bool] = None

    @property
    def query(self) -> DataRequest:
        params_emissions: DataRequestParams = {
            "drilldowns": [self.location_emissions],
            "measures": [self.measure_emissions],
        }

        if self.locale is not None:
            params_emissions["locale"] = self.locale

        return DataRequest.new(self.cube_emissions, params_emissions)

    def __getattr__(self, _name: str):
        return getattr(self.rca_params, _name)

    def _calculate(self, df: pd.DataFrame, emissions: pd.DataFrame):
        cutoff = self.cutoff
        rank = self.rank
        sort_ascending = self.sort_ascending

        index = self.rca_params.location
        columns = self.rca_params.activity

        rca, _, tbl = self.rca_params._calculate(df)

        rca[rca >= cutoff] = 1
        rca[rca < cutoff] = 0

        # Guess ID column names
        index_id = f"{index} ID"
        index_id = index_id if index_id in df.columns else index
        columns_id = f"{columns} ID"
        columns_id = columns_id if columns_id in df.columns else columns

        #prepare emissions dataframe
        location_emissions = f"{self.location_emissions} ID"
        measure_emissions = self.measure_emissions
        df_emissions = emissions[[location_emissions, measure_emissions]].set_index(location_emissions)

        peii = economic_complexity.peii(tbl=tbl, rcas=rca, emissions=df_emissions)

        def unpivot(ds: pd.DataFrame) -> pd.DataFrame:
            name = "PEII"
            ds = ds.reset_index()
            ds.rename(columns= {"peii": name}, inplace=True)

            if sort_ascending is not None:
                ds = ds.sort_values(ascending=sort_ascending)

            if rank or sort_ascending is not None:
                ds[f"{name} Ranking"] = ds[f"{name}"].rank(ascending=False)

            # restore columns labels
            if columns != columns_id:
                df_columns = df[[columns_id, columns]].set_index(columns_id)
                dict_columns = df_columns[columns].to_dict()
                ds[columns] = ds[columns_id].map(dict_columns)

            return ds

        return peii, unpivot

    def calculate(self, df: pd.DataFrame, emissions: pd.DataFrame, *, unpivot: bool = True) -> pd.DataFrame:
        peii, do_unpivot = self._calculate(df, emissions)

        return do_unpivot(peii) if unpivot else peii
