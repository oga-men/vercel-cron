import csv
import io
from datetime import datetime, timedelta
import random
from typing import List, Dict

class VisitorDataGenerator:
    def __init__(self):
        self.base_visitors = {
            "morning": 15,    # 朝の基準来店客数
            "noon": 45,       # 昼の基準来店客数
            "evening": 30,    # 夕方の基準来店客数
            "night": 8        # 夜の基準来店客数
        }
    
    def generate_sample_data(self, hours_back: int = 24) -> List[Dict]:
        """
        過去指定時間分の来店客数データを生成（15分間隔）
        
        Args:
            hours_back: 何時間前からのデータを生成するか
            
        Returns:
            List[Dict]: 来店客数データのリスト
        """
        data = []
        current_time = datetime.now()
        
        # 15分間隔で過去のデータを生成（本来の要件に合わせて）
        for i in range(hours_back * 4):  # 1時間 = 4回（15分間隔）
            timestamp = current_time - timedelta(minutes=15 * i)
            visitor_count = self._calculate_visitor_count(timestamp)
            
            data.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "date": timestamp.strftime("%Y-%m-%d"),
                "time": timestamp.strftime("%H:%M"),
                "visitor_count": visitor_count,
                "day_of_week": timestamp.strftime("%A"),
                "hour": timestamp.hour
            })
        
        # 時系列順にソート（古い順）
        data.reverse()
        return data
    
    def _calculate_visitor_count(self, timestamp: datetime) -> int:
        """
        時間帯に基づいて来店客数を計算
        
        Args:
            timestamp: 対象時刻
            
        Returns:
            int: 来店客数
        """
        hour = timestamp.hour
        
        # 時間帯による基準値設定
        if 6 <= hour < 11:
            base = self.base_visitors["morning"]
        elif 11 <= hour < 15:
            base = self.base_visitors["noon"]
        elif 15 <= hour < 20:
            base = self.base_visitors["evening"]
        else:
            base = self.base_visitors["night"]
        
        # 曜日による調整（土日は+20%）
        if timestamp.weekday() >= 5:  # 土日
            base = int(base * 1.2)
        
        # ランダム変動（±30%）
        variation = random.uniform(0.7, 1.3)
        visitor_count = max(0, int(base * variation))
        
        return visitor_count
    
    def generate_current_data(self) -> Dict:
        """
        現在時刻の来店客数データを生成
        
        Returns:
            Dict: 現在の来店客数データ
        """
        current_time = datetime.now()
        # 15分単位に切り下げ（本来の15分間隔要件に合わせて）
        minutes = (current_time.minute // 15) * 15
        adjusted_time = current_time.replace(minute=minutes, second=0, microsecond=0)
        
        visitor_count = self._calculate_visitor_count(adjusted_time)
        
        return {
            "timestamp": adjusted_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": adjusted_time.strftime("%Y-%m-%d"),
            "time": adjusted_time.strftime("%H:%M"),
            "visitor_count": visitor_count,
            "day_of_week": adjusted_time.strftime("%A"),
            "hour": adjusted_time.hour
        }

def generate_csv_data(data_type: str = "current") -> str:
    """
    CSV形式のデータを生成
    
    Args:
        data_type: "current" または "historical"
        
    Returns:
        str: CSV形式の文字列
    """
    generator = VisitorDataGenerator()
    
    if data_type == "current":
        data = [generator.generate_current_data()]
    else:
        data = generator.generate_sample_data(hours_back=24)
    
    # CSV文字列を生成
    output = io.StringIO()
    fieldnames = ["timestamp", "date", "time", "visitor_count", "day_of_week", "hour"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(data)
    
    csv_content = output.getvalue()
    output.close()
    
    return csv_content

def generate_filename() -> str:
    """
    タイムスタンプ付きのCSVファイル名を生成
    
    Returns:
        str: ファイル名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"visitor_data_{timestamp}.csv"