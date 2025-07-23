# Vercel Cron Jobs を活用したCSVファイルFTP送信システム実装レポート

## 概要

弊社の来店客数ダッシュボードサービス（Vercel + FastAPI + Supabase構成）において、GUIダッシュボードを必要としないお客様向けに、15分間隔でCSVデータをFTP送信するシステムの実装方針を調査・検討しました。

## 要件整理

- **実行間隔**: 15分おき
- **データ形式**: CSV形式
- **送信方法**: FTP
- **実行環境**: Vercel（既存のFastAPIサービスと連携）
- **データソース**: Supabase（既存の来店客数データベース）

## 技術的アプローチ

### 1. Vercel Cron Jobs の活用

#### 設定方法
プロジェクトルートに `vercel.json` を作成し、15分間隔の実行スケジュールを設定：

```json
{
  "crons": [
    {
      "path": "/api/ftp-csv-export",
      "schedule": "*/15 * * * *"
    }
  ]
}
```

#### 重要なポイント
- Cron Jobsは本番デプロイメントでのみ実行
- Vercel Functionsと同じ使用料金・制限が適用
- ダッシュボードから実行状況の監視が可能

### 2. FastAPI エンドポイントの実装

#### 基本構成
```python
from fastapi import FastAPI
from supabase import create_client
import ftplib
import pandas as pd
from io import StringIO
import os

app = FastAPI()

@app.post("/api/ftp-csv-export")
async def export_csv_to_ftp():
    # 1. Supabaseからデータ取得
    # 2. CSV形式に変換
    # 3. FTP送信
    # 4. 結果をログ出力
    pass
```

#### Vercel デプロイ設定
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

### 3. FTP送信機能の実装

#### 標準ライブラリ ftplib を使用
```python
import ftplib
from contextlib import contextmanager

@contextmanager
def ftp_connection(hostname, username, password):
    ftp = ftplib.FTP(hostname)
    try:
        ftp.login(username, password)
        yield ftp
    finally:
        ftp.close()

def upload_csv_to_ftp(csv_data, filename, ftp_config):
    with ftp_connection(
        ftp_config['hostname'],
        ftp_config['username'], 
        ftp_config['password']
    ) as ftp:
        # CSVデータをバイナリ形式で送信
        csv_bytes = csv_data.encode('utf-8')
        ftp.storbinary(f'STOR {filename}', io.BytesIO(csv_bytes))
```

#### セキュアFTP（FTPS）対応
```python
from ftplib import FTP_TLS

def secure_ftp_upload(csv_data, filename, ftp_config):
    with FTP_TLS(
        host=ftp_config['hostname'],
        user=ftp_config['username'],
        passwd=ftp_config['password']
    ) as ftp:
        ftp.storbinary(f'STOR {filename}', io.BytesIO(csv_data))
```

### 4. データ処理フロー

#### 1. Supabaseからのデータ取得
```python
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def get_visitor_data():
    response = supabase.table('visitor_counts').select('*').execute()
    return response.data
```

#### 2. CSV形式への変換
```python
import pandas as pd

def convert_to_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False)
```

#### 3. ファイル名の動的生成
```python
from datetime import datetime

def generate_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"visitor_data_{timestamp}.csv"
```

## 実装上の考慮事項

### セキュリティ
- FTP認証情報は環境変数で管理
- FTPS（FTP over TLS/SSL）の使用を推奨
- Vercelの環境変数機能を活用

### エラーハンドリング
- FTP接続エラーの処理
- データベース接続エラーの処理
- リトライ機能の実装検討

### 制限事項
- Vercel Functions のタイムアウト制限（デフォルト10秒、最大60秒）
- 関数サイズ制限（250MB）
- 同時実行数の制限

### 監視・ログ
```python
import logging

logger = logging.getLogger(__name__)

def log_export_result(success, filename, error=None):
    if success:
        logger.info(f"CSV export successful: {filename}")
    else:
        logger.error(f"CSV export failed: {filename}, Error: {error}")
```

## 必要な依存関係

```txt
fastapi
supabase
pandas
python-multipart
uvicorn
```

## デプロイメント手順

1. プロジェクトセットアップ
2. 環境変数の設定（Vercelダッシュボード）
3. vercel.json でCron設定
4. FastAPI エンドポイント実装
5. 本番環境へのデプロイ
6. Cron Job動作確認

## 想定されるメリット

- **既存インフラの活用**: 現在のVercel + FastAPI環境を最大限活用
- **運用の簡素化**: Vercelの管理画面から一元管理
- **スケーラビリティ**: Serverless関数による自動スケーリング
- **コスト効率**: 実行時間のみの課金
- **開発効率**: 上司の得意なFastAPIを使用

## 次のステップ

1. 詳細な技術仕様の作成
2. プロトタイプの実装
3. テスト環境での動作確認
4. 本番環境へのデプロイとモニタリング設定

---

**作成日**: 2025年7月23日  
**作成者**: Claude Code Assistant  
**プロジェクト**: vercel-cron FTP CSV Export System