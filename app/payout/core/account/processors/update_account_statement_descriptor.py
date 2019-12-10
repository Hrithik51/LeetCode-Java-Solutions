from structlog.stdlib import BoundLogger
from typing import Union

from app.commons.api.models import DEFAULT_INTERNAL_EXCEPTION, PaymentException
from app.commons.core.processor import OperationRequest, AsyncOperation
from app.payout.core.account import models as account_models
from app.payout.repository.maindb.model.payment_account import PaymentAccountUpdate
from app.payout.repository.maindb.payment_account import (
    PaymentAccountRepositoryInterface,
)
from app.payout.models import PayoutAccountId


class UpdatePayoutAccountStatementDescriptorRequest(OperationRequest):
    payout_account_id: PayoutAccountId
    statement_descriptor: str


class UpdatePayoutAccountStatementDescriptor(
    AsyncOperation[
        UpdatePayoutAccountStatementDescriptorRequest,
        account_models.PayoutAccountInternal,
    ]
):
    """
    Processor to create a payout account
    """

    payment_account_repo: PaymentAccountRepositoryInterface

    def __init__(
        self,
        request: UpdatePayoutAccountStatementDescriptorRequest,
        *,
        payment_account_repo: PaymentAccountRepositoryInterface,
        logger: BoundLogger = None
    ):
        super().__init__(request, logger)
        self.request = request
        self.payment_account_repo = payment_account_repo

    async def _execute(self) -> account_models.PayoutAccountInternal:
        self.logger.info(
            "[Account Update Statement Descriptor] updating account statement_descriptor",
            extra={"payment_account_id": self.request.payout_account_id},
        )
        payment_account = await self.payment_account_repo.update_payment_account_by_id(
            payment_account_id=self.request.payout_account_id,
            data=PaymentAccountUpdate(
                statement_descriptor=self.request.statement_descriptor
            ),
        )
        self.logger.info(
            "[Account Update Statement Descriptor] updated account statement_descriptor",
            extra={"payment_account_id": self.request.payout_account_id},
        )
        return account_models.PayoutAccountInternal(payment_account=payment_account)

    def _handle_exception(
        self, dep_exec: BaseException
    ) -> Union[PaymentException, account_models.PayoutAccountInternal]:
        raise DEFAULT_INTERNAL_EXCEPTION