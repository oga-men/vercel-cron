from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime
import sys
import pytz

# パスを追加してservicesモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.csv_generator import generate_csv_data, generate_filename
from services.ftp_client import upload_csv_to_ftp

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="来店客数データ自動送信API",
    description="店舗の来店客数データをCSV形式でFTP送信するAPI（現在は毎日17時実行、本来は15分間隔予定）",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Vercel Cron CSV Export API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "csv-export-api"}

@app.get("/api/cron-export")
async def cron_csv_export():
    """
    来店客数データの自動送信エンドポイント
    現在は毎日17時に実行（Vercel Hobbyプラン制限）
    本来は15分間隔での実行を想定
    """
    try:
        logger.info("Starting CSV export cron job")
        
        # 1. CSVデータを生成
        logger.info("Generating CSV data")
        csv_content = generate_csv_data(data_type="current")
        
        # 2. ファイル名を生成
        filename = generate_filename()
        logger.info(f"Generated filename: {filename}")
        
        # 3. FTP送信
        logger.info("Uploading CSV to FTP server")
        upload_result = upload_csv_to_ftp(csv_content, filename)
        
        # 4. 結果の処理
        if upload_result["success"]:
            logger.info(f"CSV export successful: {filename}")
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "CSV export completed successfully",
                    "filename": filename,
                    "timestamp": datetime.now(pytz.timezone('Asia/Tokyo')).isoformat(),
                    "upload_details": upload_result
                }
            )
        else:
            logger.error(f"CSV export failed: {upload_result.get('message', 'Unknown error')}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "CSV export failed",
                    "filename": filename,
                    "timestamp": datetime.now(pytz.timezone('Asia/Tokyo')).isoformat(),
                    "error_details": upload_result
                }
            )
            
    except Exception as e:
        error_msg = f"Unexpected error in cron job: {str(e)}"
        logger.error(error_msg)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": error_msg,
                "timestamp": datetime.now(pytz.timezone('Asia/Tokyo')).isoformat()
            }
        )

@app.get("/api/test-ftp")
async def test_ftp_connection():
    """
    FTP接続のテストエンドポイント
    """
    try:
        from services.ftp_client import FTPClient
        
        ftp_client = FTPClient()
        test_result = ftp_client.test_connection()
        
        if test_result["success"]:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "success",
                    "message": "FTP connection test successful",
                    "details": test_result
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "FTP connection test failed",
                    "details": test_result
                }
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"FTP test error: {str(e)}"
            }
        )

@app.get("/api/generate-sample-csv")
async def generate_sample_csv():
    """
    来店客数データのサンプル生成・確認用エンドポイント
    """
    try:
        # 現在のデータを生成
        current_csv = generate_csv_data(data_type="current")
        filename = generate_filename()
        
        # 過去24時間のデータも生成
        historical_csv = generate_csv_data(data_type="historical")
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "current_filename": filename,
                "current_csv_preview": current_csv[:200] + "..." if len(current_csv) > 200 else current_csv,
                "historical_csv_lines": len(historical_csv.split('\n')) - 1,  # ヘッダー除く
                "message": "Sample CSV data generated successfully"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"CSV generation error: {str(e)}"
            }
        )

@app.get("/api/manual-export")
async def manual_csv_export():
    """
    手動での来店客数データ送信エンドポイント
    テスト・デバッグ・緊急時用
    """
    return await cron_csv_export()

