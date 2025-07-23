# Vercel Cron CSV Export System

毎日17時に来店客数データをCSV形式でFTP送信するシステムです。

## プロジェクト構成

```
/vercel-cron/
├── api/
│   └── main.py          # FastAPIメインアプリケーション（全エンドポイント統合）
├── services/
│   ├── csv_generator.py # CSV生成機能（サンプルデータ）
│   └── ftp_client.py    # FTP送信機能
├── vercel.json          # Vercel設定（毎日17時Cron実行）
├── requirements.txt     # Python依存関係
├── .env.example         # 環境変数テンプレート
└── README.md            # このファイル
```

## 機能

- **自動CSV生成**: 来店客数データのサンプル生成（時間帯・曜日を考慮）
- **FTP送信**: 生成されたCSVファイルをFTPサーバーに自動送信
- **Cron実行**: Vercel Cron Jobsで毎日17時に自動実行
- **ログ出力**: 処理状況の詳細ログ
- **エラーハンドリング**: FTP接続エラーなどの適切な処理

## 環境変数設定

Vercelプロジェクトの環境変数に以下を設定してください：

### 必須設定
- `FTP_HOSTNAME`: FTPサーバーのホスト名
- `FTP_USERNAME`: FTPユーザー名
- `FTP_PASSWORD`: FTPパスワード

### オプション設定
- `FTP_PORT`: FTPポート（デフォルト: 21）
- `FTP_REMOTE_DIR`: アップロード先ディレクトリ（デフォルト: /）
- `FTP_USE_TLS`: FTPS使用の有無（デフォルト: false）

## デプロイ手順

### 1. Vercelプロジェクト作成
```bash
# Vercel CLIをインストール（まだの場合）
npm i -g vercel

# プロジェクトをデプロイ
vercel

# 環境変数を設定
vercel env add FTP_HOSTNAME
vercel env add FTP_USERNAME
vercel env add FTP_PASSWORD
```

### 2. 手動での環境変数設定
Vercelダッシュボード > Settings > Environment Variables で設定することも可能です。

### 3. デプロイメント
```bash
vercel --prod
```

## API エンドポイント

### メインエンドポイント
- `GET /` - アプリケーション状態確認
- `GET /health` - ヘルスチェック

### Cron関連エンドポイント
- `POST /api/cron-export` - CSV生成・FTP送信（Cronから自動実行）
- `GET /api/manual-export` - 手動でのCSVエクスポート（テスト用）
- `GET /api/test-ftp` - FTP接続テスト
- `GET /api/generate-sample-csv` - サンプルCSV生成・確認

## テスト手順

### 1. FTP接続テスト
```bash
curl https://your-app.vercel.app/api/test-ftp
```

### 2. サンプルCSV生成テスト
```bash
curl https://your-app.vercel.app/api/generate-sample-csv
```

### 3. 手動エクスポートテスト
```bash
curl -X GET https://your-app.vercel.app/api/manual-export
```

## Cron設定

`vercel.json`で毎日17時の実行を設定：

```json
{
  "crons": [
    {
      "path": "/api/cron-export",
      "schedule": "0 17 * * *"
    }
  ]
}
```

## CSVデータ形式

生成されるCSVファイルの形式：

```csv
timestamp,date,time,visitor_count,day_of_week,hour
2024-01-23 09:15:00,2024-01-23,09:15,12,Tuesday,9
```

## 注意事項

- Vercel Cron Jobsは本番環境でのみ動作します
- ホビープランでは1日2回までの制限があります（このアプリは1日1回実行）
- FTP認証情報は環境変数で安全に管理してください
- タイムアウト設定は60秒に設定されています
- Cronは毎日17時（UTC）に実行されます

## ログ確認

Vercelダッシュボード > Functions タブで実行ログを確認できます。