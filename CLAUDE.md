# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

このプロジェクトは、Vercel Cron Jobsを活用したCSVファイル自動FTP送信システムです。
毎日17時に来店客数データをCSV形式で生成し、指定されたFTPサーバーに自動送信します。

## Technology Stack

- **Framework**: FastAPI (Python)
- **Deployment**: Vercel
- **Cron Jobs**: Vercel Cron Jobs (毎日17時実行)
- **File Transfer**: FTP/FTPS
- **Data Generation**: サンプル来店客数データ

## Project Structure

```
/vercel-cron/
├── api/
│   └── main.py          # FastAPIメインアプリケーション（全エンドポイント統合）
├── services/
│   ├── csv_generator.py # CSV生成機能（サンプルデータ）
│   └── ftp_client.py    # FTP送信機能
├── vercel.json          # Vercel設定（毎日17時Cron実行）
├── requirements.txt     # Python依存関係
└── .env.example         # 環境変数テンプレート
```

## Environment Variables

以下の環境変数をVercelプロジェクトに設定する必要があります：

- `FTP_HOSTNAME`: FTPサーバーのホスト名
- `FTP_USERNAME`: FTPユーザー名
- `FTP_PASSWORD`: FTPパスワード
- `FTP_REMOTE_DIR`: アップロード先ディレクトリ
- `FTP_USE_TLS`: FTPS使用の有無

## Development Setup

1. 依存関係のインストール:
   ```bash
   pip install -r requirements.txt
   ```

2. 環境変数の設定:
   ```bash
   cp .env.example .env
   # .envファイルを編集してFTP情報を設定
   ```

3. ローカル実行:
   ```bash
   uvicorn api.main:app --reload
   ```

## Key Endpoints

- `GET /` - アプリケーション状態確認
- `GET /health` - ヘルスチェック
- `POST /api/cron-export` - CSV生成・FTP送信（Cronから自動実行）
- `GET /api/manual-export` - 手動でのCSVエクスポート
- `GET /api/test-ftp` - FTP接続テスト
- `GET /api/generate-sample-csv` - サンプルCSV生成・確認

## Architecture

- **FastAPI Application**: 単一のmain.pyファイルに全エンドポイントを統合
- **Cron Execution**: Vercel Cron Jobsで毎日17時に自動実行
- **Data Flow**: サンプルデータ生成 → CSV変換 → FTP送信
- **Error Handling**: 各段階でのエラーハンドリングとログ出力