# PTSNotify

PTSとTdnetを検索し、該当する銘柄をDiscordに通知する。

## 環境構築

1. 下記コマンドを実行する。

    ```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    ```

1. .envファイルにDicord通知用のwebhoook_urlを設定する。

## 実行

1. 下記コマンドを実行する。

    ```
    python pts_ranking.py
    ```

## 定期実行

1. cronを使用する。

    ```
    crontab -e
    ```

1. 一番下に以下のような設定を記載する。

    ```
    /home/katsura/ws/PTSNotify/venv/bin/python3 /home/katsura/ws/PTSNotify/pts_ranking.py
    ```