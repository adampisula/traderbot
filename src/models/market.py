from pydantic import BaseModel
from typing import List, Tuple, Dict 
from os import path, mkdir, listdir
from datetime import datetime
import plotly.graph_objects as go

from models.pair import Pair
from models.transaction import Transaction


class OHLCV(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketFrame(BaseModel):
    timestamp: datetime
    ohlcv: Dict[str, OHLCV]

    def get_pair(self, pair: Pair) -> Tuple[datetime, OHLCV]:
        return self.timestamp, self.ohlcv[str(pair)]
    
    def csv(self) -> List[str]:
        return [f"{int(self.timestamp.timestamp())},{pair},{ohlcv.open},{ohlcv.high},{ohlcv.low},{ohlcv.close},{ohlcv.volume}" for pair, ohlcv in self.ohlcv.items()]


class Market:
    frames: List[MarketFrame]
    logs: List[Tuple[datetime, str]] = []

    def __init__(self, frames: List[MarketFrame]=[]) -> None:
        self.frames = frames

    def get_all_for_pair(self, pair: Pair) -> List[Tuple[datetime, OHLCV]]:
        return [frame.get_pair(pair) for frame in self.frames]

    def log(self, text: str, timestamp: datetime = datetime.now()) -> None:
        self.logs.append((timestamp, text))

    # https://plotly.com/python-api-reference/generated/plotly.html?highlight=update#plotly.basedatatypes.BaseFigure.add_trace
    def plot_for_pair(self, pair: Pair, display=True, include_logs=True) -> go.Figure:
        pair_ohlcv = self.get_all_for_pair(pair)

        timestamps = [x[0] for x in pair_ohlcv]

        opens = [x[1].open for x in pair_ohlcv]
        highs = [x[1].high for x in pair_ohlcv]
        lows = [x[1].low for x in pair_ohlcv]
        closes = [x[1].close for x in pair_ohlcv]

        fig = go.Figure(data=[go.Candlestick(x=timestamps, open=opens, high=highs, low=lows, close=closes)])

        if include_logs:
            for log in self.logs:
                self.__plot_log(fig, log[0], log[1])

        if display:
            fig.show()

        return fig

    def __plot_log(self, fig: go.Figure, timestamp: datetime, text: str) -> None:
        fig.add_vline(
            x=int(timestamp.timestamp() * 1000),
            line_width=1,
            line_dash="dash",
            line_color="black",
            annotation_text=text
        )

    # For format="csv", filename is a directory where the CSV files will be saved
    def save_to_file(self, filename: str, format="csv") -> None:
        if format == "csv":
            if not path.exists(filename):
                mkdir(filename)

            for frame in self.frames:
                with open(path.join(filename, f"{int(frame.timestamp.timestamp())}.csv"), "w") as f:
                    f.write("timestamp,symbol,open,high,low,close,volume\n")
                    for line in frame.csv():
                        f.write(line + "\n")

        else:
            raise NotImplementedError("Only CSV format is supported")

    def import_from_file(self, filename: str, format="csv") -> None:
        if format == "csv":
            self.frames = []

            files = listdir(filename)
            sorted_files = sorted(files, key=lambda x: int(x.split(".")[0]))

            for file in sorted_files:
                with open(path.join(filename, file), "r") as f:
                    lines = f.readlines()
                    timestamp_str = lines[1].split(",")[0]
                    timestamp = int(timestamp_str) if len(timestamp_str) == 10 else int(timestamp_str) // 1000
                    ohlcv = {}
                    for line in lines[1:]:
                        parts = line.split(",")
                        ohlcv[parts[1]] = OHLCV(
                            open=float(parts[2]),
                            high=float(parts[3]),
                            low=float(parts[4]),
                            close=float(parts[5]),
                            volume=float(parts[6]),
                        )
                    try:
                        self.frames.append(MarketFrame(timestamp=datetime.fromtimestamp(timestamp), ohlcv=ohlcv))
                    except Exception as e:
                        print(e)
        else:
            raise NotImplementedError("Only CSV format is supported")