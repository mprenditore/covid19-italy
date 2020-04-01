import datetime
import pandas as pd
from typing import List
from config import Config
from translation import Translate
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=60)


@cached(cache)
class Data:
    data = None
    aggregated_data = None
    total_regions_data = None
    regions_data = None
    regions_list = None
    t = None
    source = None
    source_config = None
    n_days = 0
    features = []
    extended_features = []
    latest_update = "1970-01-01 00:00:00"

    def __init__(self, source: str, lang: str = "English"):
        self.source = source
        self.source_config = Config().sources.get(self.source)
        self.t = Translate(lang)
        self.data = getattr(self, "get_data_" + self.source,
                            pd.DataFrame)()
        if self.data.empty:
            return
        self.normalize_date()
        self.set_latest_update()
        self.data = self.calculate_days_passed(self.data)
        self.set_features(self.source_config['no_feature_columns'])
        # Remove the time and just focus on the date
        self.aggregate_data()
        self.set_total_regions_data()
        self.set_regions_data()
        self.set_regions_list()

    def get_data_ita(self):
        _data = pd.read_csv(self.source_config['csv'][0])
        _data = _data.rename(columns={
            "data": "date",
            "stato": "state",
            "codice_regione": "region_code",
            "denominazione_regione": "region_name",
            "ricoverati_con_sintomi": "feature_hospitalized_with_symptoms",
            "terapia_intensiva": "feature_people_in_icu",
            "totale_ospedalizzati": "feature_total_hospitalized",
            "isolamento_domiciliare": "feature_people_in_domestic_isolation",
            "totale_positivi": "feature_total_positives",
            "nuovi_positivi": "feature_new_positives",
            "variazione_totale_positivi": "feature_variation_total_positives",
            "dimessi_guariti": "feature_people_discharged_and_recovered",
            "deceduti": "feature_deaths",
            "totale_casi": "feature_total_cases",
            "tamponi": "feature_total_tests"
        })
        return _data

    def get_data_glo(self):
        all_data = []
        for csv in self.source_config['csv']:
            _data = (pd.read_csv(csv['url']))
            _data = _data.rename(columns={
                'Province/State': "state",
                "Country/Region": "region_name",
                "Lat": "lat",
                "Long": "long"
            })
            _data = _data.melt(
                id_vars=["state", "region_name", "lat", "long"],
                var_name="date",
                value_name=csv['column'])
            _data = _data.loc[_data[csv['column']] > 0]
            _data = _data[[
                "date", "state", "region_name", "lat", "long", csv['column']]]
            all_data.append(_data)
        _data = pd.merge(all_data[0], all_data[1], how='left',
                         on=['date', 'state', 'region_name',
                             'lat', 'long'])
        return _data

    def normalize_date(self):
        self.data["date"] = pd.to_datetime(
            self.data["date"]).apply(lambda x: x.date())
        return self.data

    def set_latest_update(self):
        self.latest_update = self.data.tail(1)["date"].values[0]
        return

    def set_features(self, columns: List[str]) -> List[str]:
        """
        Gets features from data, i.e. all columns except date, state,
            region_code, region_name, lat, long
        """
        self.features = self.data.drop(
            columns=columns
        ).columns.tolist()
        return

    def calculate_delta(self, data, feature: str):
        suffix = "delta"
        data[f"{feature}_{suffix}"] = data[feature].diff()
        self.extended_features.append(f"{feature}_{suffix}")
        return data

    def calculate_growth(self, data, feature: str):
        suffix = "growth"
        yesterday_val = data[feature].shift()
        data[f"{feature}_{suffix}"] = (
                data[feature] / yesterday_val
            )
        self.extended_features.append(f"{feature}_{suffix}")
        return data

    def calculate_days_passed(self, data):
        data["days_passed"] = data["date"].apply(
            lambda x: (x - datetime.date(2020, 2, 24)).days
        )
        self.n_days = data["days_passed"].unique().shape[0] - 1
        return data

    def aggregate_data(self):
        self.extended_features = self.features.copy()
        self.aggregated_data = self.data.groupby("date", as_index=False).sum()
        for feature in self.features:
            self.aggregated_data = self.calculate_delta(
                self.aggregated_data, feature)
            self.aggregated_data = self.calculate_growth(
                self.aggregated_data, feature)
        self.aggregated_data = self.calculate_days_passed(self.aggregated_data)
        self.aggregated_data = self.aggregated_data.dropna()
        return self.aggregated_data

    def get_on_days_passed(self, data, days):
        return data[data["days_passed"] == days]

    def set_total_regions_data(self):
        self.total_regions_data = self.data.groupby(
            ["date", "region_name"], as_index=False
        ).sum()
        return

    def set_regions_data(self):
        self.regions_data = self.total_regions_data.groupby("region_name")
        return

    def get_regions_default(self, feature: str):
        return self.regions_data.max().sort_values(
            feature).tail(self.source_config.get(
                "def_regions_count", 5)).index.tolist()

    def set_regions_list(self):
        self.regions_list = self.data["region_name"].unique().tolist()
        return

    def get_selected_regions_data(self, regions: List[str]):
        _selected_regions = self.total_regions_data[
            self.total_regions_data["region_name"].isin(regions)
        ]
        regions_array = []
        for _, region in _selected_regions.groupby("region_name"):
            region = region.sort_values("date")
            for feature in self.features:
                region = self.calculate_delta(region, feature)
                region = self.calculate_growth(region, feature)
            regions_array.append(region)
        if len(regions_array) == 0:
            return pd.DataFrame()
        return pd.concat(regions_array).reset_index(drop=True)
