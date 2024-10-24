import enum
import json
from re import A
import typing
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Tuple, Dict 
from os import path, mkdir, listdir
from datetime import datetime
import plotly.graph_objects as go

from models import symbol
from models.symbol import Symbol
from models.transaction import OperationEnum, Transaction


class OHLCV(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketFrame(BaseModel):
    timestamp: datetime
    ohlcv: Dict[str, OHLCV]

    def get_symbol(self, symbol: Symbol) -> Tuple[datetime, OHLCV]:
        return self.timestamp, self.ohlcv[str(symbol)]
    
    def csv_header(self) -> str:
        return "timestamp,symbol,open,high,low,close,volume"

    def csv(self) -> List[str]:
        return [f"{int(self.timestamp.timestamp())},{symbol},{ohlcv.open},{ohlcv.high},{ohlcv.low},{ohlcv.close},{ohlcv.volume}" for symbol, ohlcv in self.ohlcv.items()]

class LogType(enum.Enum):
    JSON = "json"
    STRING = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False

class Log(BaseModel):
    timestamp: datetime
    type: LogType = Field(default=LogType.STRING)
    value: str | dict
    symbol: Optional[Symbol] = None

    def value_str(self) -> str:
        if self.type == LogType.JSON:
            return "`json`" + json.dumps(self.value)
        return typing.cast(str, self.value)

class FunctionPlot(BaseModel):
    timestamp: datetime
    label: str
    value: float
    color: str
    symbol: Optional[Symbol] = None

class OutputFrame(BaseModel):
    timestamp: datetime
    logs: List[Log]
    transactions: List[Transaction]
    function_plots: List[FunctionPlot]

    def csv_header(self) -> str:
        # Columns:
        # log_timestamp, log_value, log_symbol
        # transaction_timestamp, transaction_operation, transaction_symbol, transaction_notes 
        # function_plot_timestamp, function_plot_label, function_plot_value, function_plot_color, function_plot_symbol
        return "log_timestamp,log_value,log_symbol,transaction_timestamp,transaction_operation,transaction_symbol,transaction_notes,function_plot_timestamp,function_plot_label,function_plot_value,function_plot_color,function_plot_symbol"

    def csv(self) -> List[str]:
        def csv_row(x: Log | Transaction | FunctionPlot) -> str:
            if isinstance(x, Log):
                return f"{int(x.timestamp.timestamp())},{x.value_str()},{x.symbol if x.symbol else ""},,,,,,,,,"
            elif isinstance(x, Transaction):
                return f",,,{int(x.timestamp.timestamp())},{x.operation},{x.symbol},{x.notes if x.notes else ""},,,,,"
            elif isinstance(x, FunctionPlot):
                return f",,,,,,,{int(x.timestamp.timestamp())},{x.label},{x.value},{x.color},{x.symbol if x.symbol else ""}"

        rows = [csv_row(x) for x in self.logs + self.transactions + self.function_plots]

        return rows

class Market:
    _frames: List[MarketFrame | Tuple[MarketFrame, OutputFrame]]

    def __init__(self, frames: List[MarketFrame | Tuple[MarketFrame, OutputFrame]]=[]) -> None:
        self._frames = frames

    def get_all_symbol_data(self, symbol: Symbol) -> List[Tuple[datetime, OHLCV]]:
        data: List[Tuple[datetime, OHLCV]] = []

        for frame in self._frames:
            if isinstance(frame, MarketFrame):
                data += [frame.get_symbol(symbol)]
            elif isinstance(frame, tuple) and isinstance(frame[0], MarketFrame):
                data += [frame[0].get_symbol(symbol)]
            
        return data

    def add_frame(self, frame: MarketFrame | Tuple[MarketFrame, OutputFrame]) -> None:
        self._frames.append(frame)

    # https://plotly.com/python-api-reference/generated/plotly.html?highlight=update#plotly.basedatatypes.BaseFigure.add_trace
    def plot_for_symbol(
            self,
            symbol: Symbol,
            display=True,
            include_logs=True,
            include_transactions=True,
            include_function_plots=True,
        ) -> go.Figure:
        symbol_ohlcv = self.get_all_symbol_data(symbol)

        timestamps = [x[0] for x in symbol_ohlcv]

        opens = [x[1].open for x in symbol_ohlcv]
        highs = [x[1].high for x in symbol_ohlcv]
        lows = [x[1].low for x in symbol_ohlcv]
        closes = [x[1].close for x in symbol_ohlcv]

        fig = go.Figure(data=[go.Candlestick(x=timestamps, open=opens, high=highs, low=lows, close=closes)])

        logs: List[Log] = []
        transactions: List[Transaction] = []
        function_plots: List[FunctionPlot] = []

        for frame in self._frames:
            if include_logs and isinstance(frame, tuple) and isinstance(frame[1], OutputFrame):
                logs += frame[1].logs
            if include_transactions and isinstance(frame, tuple) and isinstance(frame[1], OutputFrame):
                transactions += frame[1].transactions
            if include_function_plots and isinstance(frame, tuple) and isinstance(frame[1], OutputFrame):
                function_plots += frame[1].function_plots

        for log in logs:
            self.__plot_log(fig, symbol, log)

        for transaction in transactions:
            self.__plot_transaction(fig, symbol, transaction)

        for function_plot in function_plots:
            self.__plot_function_plot(fig, symbol, function_plot)

        if display:
            fig.show()

        return fig

    def __plot_log(self, fig: go.Figure, symbol: Optional[Symbol], log: Log) -> None:
        if log.symbol and symbol != log.symbol:
            return

        annotation_text: Optional[str] = None

        if log.type == LogType.STRING:
            annotation_text = typing.cast(str, log.value)
        elif log.type == LogType.JSON:
            annotation_text = "`json`" + json.dumps(typing.cast(dict, log.value))

        fig.add_vline(
            x=int(log.timestamp.timestamp() * 1000),
            line_width=1,
            line_dash="dash",
            line_color="black",
            annotation_text=annotation_text,
        )

    def __plot_transaction(self, fig: go.Figure, symbol: Optional[Symbol], transaction: Transaction) -> None:
        if transaction.symbol != symbol:
            return

        color: str

        if transaction.operation == OperationEnum.BUY:
            color = "green"
        elif transaction.operation == OperationEnum.SELL:
            color = "red"
        else:
            color = "blue"

        fig.add_vline(
            x=int(transaction.timestamp.timestamp() * 1000),
            line_width=1,
            line_color=color,
            annotation_text=transaction.notes or "",
            annotation_align="left",
        )

    def __plot_function_plot(self, fig: go.Figure, symbol: Optional[Symbol], function_plot: FunctionPlot) -> None:  # doesn't work yet, probably best to add to a list and draw all at once at the end
        pass

        # if function_plot.symbol and function_plot.symbol != symbol:
        #     return
        # fig.add_trace(go.Scatter(
        #     x=int(function_plot.timestamp.timestamp() * 1000),
        #     y=function_plot.value,
        #     name=function_plot.label,
        #     # line_width=1,
        #     # line_dash="dash",
        #     line=go.scatter.Line(color=function_plot.color),
        #     # line_color=function_plot.color,
        # ))

    # For format="csv", filename is a directory where the CSV files will be saved
    def save_to_file(self, filename: str, format="csv") -> None:
        if format == "csv":
            if not path.exists(filename):
                mkdir(filename)

            for frame in self._frames:
                if isinstance(frame, tuple) and isinstance(frame[1], OutputFrame):
                    with open(path.join(filename, f"{int(frame[1].timestamp.timestamp())}.of.csv"), "w") as f:
                        f.write(frame[1].csv_header() + "\n")
                        for line in frame[1].csv():
                            f.write(line + "\n")
                if isinstance(frame, MarketFrame) or (isinstance(frame, tuple) and isinstance(frame[0], MarketFrame)):
                    mf = frame[0] if isinstance(frame, tuple) else frame
                    with open(path.join(filename, f"{int(mf.timestamp.timestamp())}.mf.csv"), "w") as f:
                        f.write(f"{mf.csv_header()}\n")
                        for line in mf.csv():
                            f.write(line + "\n")

        else:
            raise NotImplementedError("Only CSV format is supported")

    def import_from_file(self, filename: str, format="csv") -> None:
        if format == "csv":
            self._frames = []

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
                        self._frames.append(MarketFrame(timestamp=datetime.fromtimestamp(timestamp), ohlcv=ohlcv))
                    except Exception as e:
                        print(e)
        else:
            raise NotImplementedError("Only CSV format is supported")