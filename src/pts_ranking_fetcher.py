import pandas as pd
import requests
from io import StringIO

PTS_RANKING_URL = "https://kabu.hayauma.net/ranking/pts-rate-high/"

REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

class PtsRankingFetcher:
    def fetch_pts_ranking(self) -> pd.DataFrame:
        """
        PTS値上がり率ランキングを取得し、整形してDataFrameとして返す。
        """
        print("Fetching PTS ranking data...")
        try:
            r = requests.get(PTS_RANKING_URL, headers=REQUEST_HEADER)
            r.raise_for_status()
            r.encoding = 'utf-8'

            df_list = pd.read_html(StringIO(r.text))
            if not df_list:
                print("No tables found on PTS ranking page.")
                return pd.DataFrame()

            df = df_list[0].copy()
            # カラム名を整形
            df = df.rename(columns={"終値比.1": "前日比率"})
            df = df[["コード", "銘柄名", "前日比率", "出来高"]]

            # データクレンジング
            df["前日比率"] = df["前日比率"].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
            df["出来高"] = df["出来高"].astype(str).str.replace(r'[^\d]', '', regex=True).astype(float)
            df["コード"] = df["コード"].astype(str)

            print("Successfully fetched and processed PTS ranking data.")
            return df

        except requests.exceptions.RequestException as e:
            print(f"Error fetching PTS data: {e}")
        except (ValueError, KeyError, IndexError) as e:
            print(f"Error processing PTS data: {e}")

        return pd.DataFrame()
