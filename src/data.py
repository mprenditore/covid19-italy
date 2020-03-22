import datetime
import pandas as pd
from typing import List
from translation import Translate
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=60)


@cached(cache)
class Data:
    csv_url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    data = None
    aggregated_data = None
    total_regions_data = None
    regions_data = None
    regions_list = None
    t = None
    n_days = 0
    features = []
    extended_features = []
    latest_update = "1970-01-01 00:00:00"

    def __init__(self, lang: str = "English"):
        self.data = self.get_data()
        self.features = self.get_features()
        self.t = Translate(lang)

    def get_data(self):
        self.data = pd.read_csv(self.csv_url)
        self.normalize_data_pcm_dpc()
        self.get_latest_update()
        self.normalize_date()
        # Remove the time and just focus on the date
        self.data = self.calculate_days_passed(self.data)
        self.get_features()
        self.aggregate_data()
        self.get_total_regions_data()
        self.get_regions_data()
        self.get_regions_list()
        return self.data

    def normalize_data_pcm_dpc(self):
        self.data = self.data.rename(columns={
            "data": "date",
            "stato": "state",
            "codice_regione": "region_code",
            "denominazione_regione": "region_name",
            "ricoverati_con_sintomi": "feature_hospitalized_with_symptoms",
            "terapia_intensiva": "feature_people_in_icu",
            "totale_ospedalizzati": "feature_total_hospitalized",
            "isolamento_domiciliare": "feature_people_in_domestic_isolation",
            "totale_attualmente_positivi": "feature_total_current_positives",
            "nuovi_attualmente_positivi": "feature_new_current_positives",
            "dimessi_guariti": "feature_people_discharged_and_recovered",
            "deceduti": "feature_deaths",
            "totale_casi": "feature_total_cases",
            "tamponi": "feature_total_tests"
        })
        return self.data

    def normalize_date(self):
        self.data["date"] = pd.to_datetime(
            self.data["date"]).apply(lambda x: x.date())
        return self.data

    def get_latest_update(self):
        self.latest_update = self.data.tail(1)["date"].values[0]
        return self.latest_update

    def get_features(self) -> List[str]:
        """
        Gets features from data, i.e. all columns except date, state,
            region_code, region_name, lat, long
        """
        self.features = self.data.drop(
            columns=[
                "date",
                "state",
                "region_code",
                "region_name",
                "lat",
                "long",
                "days_passed"
            ]
        ).columns.tolist()
        return self.features

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

    def get_total_regions_data(self):
        self.total_regions_data = self.data.groupby(
            ["date", "region_name"], as_index=False
        ).sum()
        return self.total_regions_data

    def get_regions_data(self):
        self.regions_data = self.total_regions_data.groupby("region_name")
        return self.regions_data

    def get_regions_list(self):
        self.regions_list = self.data["region_name"].unique().tolist()
        return self.regions_list

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
