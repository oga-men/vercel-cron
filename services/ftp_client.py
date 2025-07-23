import ftplib
import io
import os
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any

# ログ設定
logger = logging.getLogger(__name__)

class FTPClient:
    def __init__(self, config: Optional[Dict[str, str]] = None):
        """
        FTPクライアントの初期化
        
        Args:
            config: FTP接続設定。Noneの場合は環境変数から取得
        """
        if config:
            self.config = config
        else:
            self.config = {
                "hostname": os.getenv("FTP_HOSTNAME"),
                "username": os.getenv("FTP_USERNAME"),
                "password": os.getenv("FTP_PASSWORD"),
                "port": int(os.getenv("FTP_PORT", "21")),
                "remote_dir": os.getenv("FTP_REMOTE_DIR", "/"),
                "use_tls": os.getenv("FTP_USE_TLS", "false").lower() == "true"
            }
        
        # 設定値の検証
        self._validate_config()
    
    def _validate_config(self):
        """FTP設定の検証"""
        required_fields = ["hostname", "username", "password"]
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"FTP configuration missing: {field}")
    
    @contextmanager
    def ftp_connection(self):
        """
        FTP接続のコンテキストマネージャー
        
        Yields:
            ftplib.FTP or ftplib.FTP_TLS: FTP接続オブジェクト
        """
        ftp = None
        try:
            # TLS使用の場合はFTP_TLS、そうでなければ通常のFTPを使用
            if self.config["use_tls"]:
                ftp = ftplib.FTP_TLS()
                logger.info("Using FTP_TLS connection")
            else:
                ftp = ftplib.FTP()
                logger.info("Using standard FTP connection")
            
            # 接続
            logger.info(f"Connecting to {self.config['hostname']}:{self.config['port']}")
            ftp.connect(self.config["hostname"], self.config["port"])
            
            # ログイン
            ftp.login(self.config["username"], self.config["password"])
            logger.info(f"Logged in as {self.config['username']}")
            
            # TLSの場合はデータ接続の暗号化を有効化
            if self.config["use_tls"]:
                ftp.prot_p()
            
            # パッシブモードを有効化（ファイアウォール対応）
            ftp.set_pasv(True)
            
            # リモートディレクトリに移動
            if self.config["remote_dir"] != "/":
                ftp.cwd(self.config["remote_dir"])
                logger.info(f"Changed directory to {self.config['remote_dir']}")
            
            yield ftp
            
        except ftplib.all_errors as e:
            logger.error(f"FTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            if ftp:
                try:
                    ftp.quit()
                    logger.info("FTP connection closed")
                except:
                    logger.warning("Error closing FTP connection")
    
    def upload_csv_string(self, csv_content: str, filename: str) -> Dict[str, Any]:
        """
        CSV文字列をFTPサーバーにアップロード
        
        Args:
            csv_content: CSV形式の文字列
            filename: アップロード先のファイル名
            
        Returns:
            Dict[str, Any]: アップロード結果
        """
        try:
            with self.ftp_connection() as ftp:
                # CSV文字列をバイトストリームに変換
                csv_bytes = csv_content.encode('utf-8')
                csv_stream = io.BytesIO(csv_bytes)
                
                # ファイルアップロード
                logger.info(f"Uploading file: {filename}")
                result = ftp.storbinary(f'STOR {filename}', csv_stream)
                
                if result.startswith('226'):  # 226 = Transfer complete
                    logger.info(f"Upload successful: {filename}")
                    return {
                        "success": True,
                        "filename": filename,
                        "size_bytes": len(csv_bytes),
                        "message": "Upload completed successfully"
                    }
                else:
                    logger.warning(f"Upload may have failed: {result}")
                    return {
                        "success": False,
                        "filename": filename,
                        "message": f"Unexpected FTP response: {result}"
                    }
                    
        except ftplib.all_errors as e:
            error_msg = f"FTP upload failed: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error during upload: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "filename": filename,
                "error": str(e),
                "message": error_msg
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        FTP接続のテスト
        
        Returns:
            Dict[str, Any]: 接続テスト結果
        """
        try:
            with self.ftp_connection() as ftp:
                # 現在のディレクトリを取得
                current_dir = ftp.pwd()
                
                # ディレクトリリストを取得（最初の5つのみ）
                file_list = []
                try:
                    file_list = ftp.nlst()[:5]
                except:
                    file_list = ["(unable to list files)"]
                
                logger.info("FTP connection test successful")
                return {
                    "success": True,
                    "current_directory": current_dir,
                    "sample_files": file_list,
                    "message": "Connection test successful"
                }
                
        except Exception as e:
            error_msg = f"FTP connection test failed: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": str(e),
                "message": error_msg
            }
    
    def create_directory_if_not_exists(self, directory: str) -> bool:
        """
        指定されたディレクトリが存在しない場合は作成
        
        Args:
            directory: 作成するディレクトリパス
            
        Returns:
            bool: 作成成功の場合True
        """
        try:
            with self.ftp_connection() as ftp:
                try:
                    ftp.cwd(directory)
                    logger.info(f"Directory already exists: {directory}")
                    return True
                except ftplib.error_perm:
                    # ディレクトリが存在しない場合は作成
                    ftp.mkd(directory)
                    logger.info(f"Created directory: {directory}")
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False

def upload_csv_to_ftp(csv_content: str, filename: str, config: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    CSV文字列をFTPサーバーにアップロードする便利関数
    
    Args:
        csv_content: CSV形式の文字列
        filename: アップロード先のファイル名
        config: FTP接続設定（Noneの場合は環境変数から取得）
        
    Returns:
        Dict[str, Any]: アップロード結果
    """
    ftp_client = FTPClient(config)
    return ftp_client.upload_csv_string(csv_content, filename)