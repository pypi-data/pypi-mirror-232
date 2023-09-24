from typing import Dict, List

from weathon.quantization.converter.position_holding import PositionHolding
from weathon.quantization.datamodel import PositionData, TradeData, OrderData, OrderRequest, ContractData
from weathon.quantization.utils.constants import Exchange


class OffsetConverter:
    """"""

    def __init__(self, main_engine: "MainEngine") -> None:
        """"""
        self.holdings: Dict[str, "PositionHolding"] = {}

        self.get_contract = main_engine.get_contract

    def update_position(self, position: PositionData) -> None:
        """"""
        if not self.is_convert_required(position.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(position.vt_symbol)
        holding.update_position(position)

    def update_trade(self, trade: TradeData) -> None:
        """"""
        if not self.is_convert_required(trade.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(trade.vt_symbol)
        holding.update_trade(trade)

    def update_order(self, order: OrderData) -> None:
        """"""
        if not self.is_convert_required(order.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(order.vt_symbol)
        holding.update_order(order)

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """"""
        if not self.is_convert_required(req.vt_symbol):
            return

        holding: PositionHolding = self.get_position_holding(req.vt_symbol)
        holding.update_order_request(req, vt_orderid)

    def get_position_holding(self, vt_symbol: str) -> "PositionHolding":
        """"""
        holding: PositionHolding = self.holdings.get(vt_symbol, None)
        if not holding:
            contract: ContractData = self.get_contract(vt_symbol)
            holding = PositionHolding(contract)
            self.holdings[vt_symbol] = holding
        return holding

    def convert_order_request(
        self,
        req: OrderRequest,
        lock: bool,
        net: bool = False
    ) -> List[OrderRequest]:
        """"""
        if not self.is_convert_required(req.vt_symbol):
            return [req]

        holding: PositionHolding = self.get_position_holding(req.vt_symbol)

        if lock:
            return holding.convert_order_request_lock(req)
        elif net:
            return holding.convert_order_request_net(req)
        elif req.exchange in {Exchange.SHFE, Exchange.INE}:
            return holding.convert_order_request_shfe(req)
        else:
            return [req]

    def is_convert_required(self, vt_symbol: str) -> bool:
        """
        Check if the contract needs offset convert.
        """
        contract: ContractData = self.get_contract(vt_symbol)

        # Only contracts with long-short position mode requires convert
        if not contract:
            return False
        elif contract.net_position:
            return False
        else:
            return True