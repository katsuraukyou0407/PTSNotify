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