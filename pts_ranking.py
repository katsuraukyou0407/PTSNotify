import os
from dotenv import load_dotenv

from src.pts_ranking_fetcher import PtsRankingFetcher
from src.tdnet_fetcher import TdnetFetcher
from src.date_calculator import DateCalculator
from src.discord_notifier import DiscordNotifier

# 抽出条件の閾値
PTS_MIN_RATE_INCREASE = 5.0  # 前日比率の最小値 (%)
PTS_MIN_VOLUME = 500.0       # 出来高の最小値 (株)

def main():
    """
    メイン処理
    """
    load_dotenv() # Load environment variables from .env file
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if not discord_webhook_url:
        print("Error: DISCORD_WEBHOOK_URL environment variable not set.")
        return

    date_calculator = DateCalculator()
    target_date = date_calculator.get_target_business_date()
    if not target_date:
        return
    
    pts_ranking_fetcher = PtsRankingFetcher()
    df_pts = pts_ranking_fetcher.fetch_pts_ranking()

    tdnet_fetcher = TdnetFetcher()
    df_tdnet = tdnet_fetcher.fetch_tdnet_disclosures(target_date.strftime("%Y%m%d"))

    if df_pts.empty or df_tdnet.empty:
        print("Required data could not be fetched. Terminating.")
        return

    tdnet_codes_with_xbrl = df_tdnet.dropna(subset=['XBRL'])['コード'].str[:4].unique().tolist()

    df_filtered = df_pts[
        (df_pts["コード"].isin(tdnet_codes_with_xbrl)) &
        (df_pts["前日比率"] > PTS_MIN_RATE_INCREASE) &
        (df_pts["出来高"] > PTS_MIN_VOLUME)
    ]

    if df_filtered.empty:
        print("No stocks met the criteria for notification.")
        return

    print(f"Found {len(df_filtered)} stocks to notify.")
    
    messages = []
    list_codes = []
    for _, row in df_filtered.iterrows():
        list_codes.append(row['コード'])
        message = (
            f"[{row['コード']}] {row['銘柄名']}\n"
            f"  - 前日比率: {row['前日比率']:.2f}% 出来高: {int(row['出来高'])}株"
        )
        messages.append(message)
    
    full_notification = "📈 **注目PTS銘柄** 📈\n\n" + "\n\n".join(messages)
    discord_notifier = DiscordNotifier(discord_webhook_url)
    discord_notifier.send_discord_notify(full_notification)
    codes_notification = "\n\n".join(list_codes)
    discord_notifier.send_discord_notify(codes_notification)

if __name__ == "__main__":
    main()
