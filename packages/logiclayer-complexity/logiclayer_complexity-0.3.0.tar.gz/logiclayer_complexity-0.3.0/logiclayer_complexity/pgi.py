from dataclasses import dataclass, field
from typing import Optional
from tesseract_olap import DataRequest, DataRequestParams

import economic_complexity
import pandas as pd

from .rca import RcaParameters


@dataclass
class PGIParameters:
    rca_params: RcaParameters
    cube_gini: str
    measure_gini: str
    location_gini: str
    cutoff: float
    rank: bool = field(default=False)
    sort_ascending: Optional[bool] = None
    
    @property
    def query(self) -> DataRequest:
        params_gini: DataRequestParams = {
            "drilldowns": [self.location_gini],
            "measures": [self.measure_gini],
        }

        if self.locale is not None:
            params_gini["locale"] = self.locale

        return DataRequest.new(self.cube_gini, params_gini)

    def __getattr__(self, _name: str):
        return getattr(self.rca_params, _name)

    def _calculate(self, df: pd.DataFrame, gini: pd.DataFrame):
        cutoff = self.cutoff
        rank = self.rank
        sort_ascending = self.sort_ascending

        index = self.rca_params.location
        columns = self.rca_params.activity
        measure = self.rca_params.measure

        rca, _, tbl = self.rca_params._calculate(df)

        rca[rca >= cutoff] = 1
        rca[rca < cutoff] = 0

        # Guess ID column names
        index_id = f"{index} ID"
        index_id = index_id if index_id in df.columns else index
        columns_id = f"{columns} ID"
        columns_id = columns_id if columns_id in df.columns else columns

        #prepare gini dataframe
        location_gini = f"{self.location_gini} ID" 
        measure_gini = self.measure_gini
        df_gini = gini[[location_gini, measure_gini]].set_index(location_gini)

        pgi = economic_complexity.pgi(tbl=tbl, rcas=rca, gini=df_gini)

        def unpivot(ds: pd.DataFrame) -> pd.DataFrame:
            name = "PGI"
            ds = ds.reset_index()
            ds.rename(columns= {"pgi": "PGI"}, inplace=True)

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

        return pgi, unpivot

    def calculate(self, df: pd.DataFrame, gini: pd.DataFrame, *, unpivot: bool = True) -> pd.DataFrame:
        pgi, do_unpivot = self._calculate(df, gini)

        return do_unpivot(pgi) if unpivot else pgi
