import dataclasses

from nibiru.pytypes import Coin, PythonMsg
from nibiru_proto.cosmos.distribution.v1beta1 import tx_pb2 as pb_distribution
from nibiru_proto.cosmos.staking.v1beta1 import tx_pb2 as pb_staking


class MsgsStaking:
    """
    Messages for the x/staking and x/distribution modules.

    Methods:
    - delegate: Delegate tokens to a validator
    - undelegate: Undelegate tokens from a validator
    - withdraw_delegator_reward: Withdraw the reward from a validator
    """

    @staticmethod
    def delegate(
        validator_address: str,
        amount: float,
    ) -> 'MsgDelegate':
        """
        Delegate tokens to a validator

        Attributes:
            validator_address: str
            amount: float

        Returns:
            MsgDelegate: PythonMsg for type 'cosmos.staking.v1beta1.MsgDelegate'
        """
        return MsgDelegate(
            validator_address=validator_address,
            amount=amount,
        )

    @staticmethod
    def undelegate(
        validator_address: str,
        amount: float,
    ) -> 'MsgUndelegate':
        """
        Undelegate tokens from a validator

        Attributes:
            validator_address (str): Bech32 valoper address
            amount (float): Amount of unibi to undelegate.
        """
        return MsgUndelegate(
            validator_address=validator_address,
            amount=amount,
        )

    @staticmethod
    def withdraw_delegator_reward(
        validator_address: str,
    ) -> 'MsgWithdrawDelegatorReward':
        """TODO
        Withdraw the reward from a validator

        Attributes:
            validator_address (str)

        Returns:
            MsgWithdrawDelegatorReward: _description_
        """
        return MsgWithdrawDelegatorReward(validator_address=validator_address)


@dataclasses.dataclass
class MsgDelegate(PythonMsg):
    """
    Delegate tokens to a validator

    Attributes:
        validator_address: str
        amount: float
    """

    validator_address: str
    amount: float

    def to_pb(self, sender: str) -> pb_staking.MsgDelegate:
        """
        Returns the Message as protobuf object.

        Returns:
            staking_pb.MsgDelegate: The proto object.

        """
        return pb_staking.MsgDelegate(
            delegator_address=sender,
            validator_address=self.validator_address,
            amount=Coin(self.amount, "unibi").to_pb(),
        )


@dataclasses.dataclass
class MsgUndelegate(PythonMsg):
    """
    Undelegate tokens from a validator

    Attributes:
        validator_address: str
        amount: float
    """

    validator_address: str
    amount: float

    def to_pb(self, sender: str) -> pb_staking.MsgUndelegate:
        """
        Returns the Message as protobuf object.

        Returns:
            staking_pb.MsgUndelegate: The proto object.

        """
        return pb_staking.MsgUndelegate(
            delegator_address=sender,
            validator_address=self.validator_address,
            amount=Coin(self.amount, "unibi").to_pb(),
        )


@dataclasses.dataclass
class MsgWithdrawDelegatorReward(PythonMsg):
    """
    Withdraw the reward from a validator

    Attributes:
        validator_address (str)
    """

    validator_address: str

    def to_pb(self, sender: str) -> pb_distribution.MsgWithdrawDelegatorReward:
        """
        Returns the Message as protobuf object.

        Returns:
            tx_pb.MsgWithdrawDelegatorReward: The proto object.

        """
        return pb_distribution.MsgWithdrawDelegatorReward(
            delegator_address=sender,
            validator_address=self.validator_address,
        )
