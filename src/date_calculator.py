from datetime import date, timedelta
import jpholiday

class DateCalculator:
    def get_target_business_date(self) -> date | None:
        """
        処理対象となる直近の営業日（スクリプト実行日の前日）を返す。
        前日が非営業日の場合はNoneを返す。
        """
        target_dt = date.today() - timedelta(days=1)
        if target_dt.weekday() >= 5 or jpholiday.is_holiday(target_dt):
            print(f"Target date {target_dt} is a holiday. Skipping process.")
            return None
        return target_dt
