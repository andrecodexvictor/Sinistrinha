from decimal import Decimal

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Transaction
from apps.users.models import UserProfile
from .serializers import TransactionSerializer, DepositWithdrawSerializer


class DepositView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']

            with transaction.atomic():
                user_profile = (
                    UserProfile.objects
                    .select_for_update()
                    .get(user=request.user)
                )
                user_profile.balance += amount
                user_profile.save(update_fields=['balance'])

                tx = Transaction.objects.create(
                    user=user_profile,
                    amount=amount,
                    transaction_type=Transaction.TransactionType.DEPOSIT,
                    status=Transaction.TransactionStatus.COMPLETED,
                )

            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(views.APIView):
    """
    Withdraw funds.
    
    Funds are frozen (deducted) only inside an atomic transaction that also
    creates the PENDING record. If either fails, both are rolled back — no
    money is lost.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']

            try:
                with transaction.atomic():
                    user_profile = (
                        UserProfile.objects
                        .select_for_update()
                        .get(user=request.user)
                    )

                    if user_profile.balance < amount:
                        return Response(
                            {"error": "Saldo insuficiente"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Deduct balance AND create record atomically
                    user_profile.balance -= amount
                    user_profile.save(update_fields=['balance'])

                    tx = Transaction.objects.create(
                        user=user_profile,
                        amount=amount,
                        transaction_type=Transaction.TransactionType.WITHDRAW,
                        status=Transaction.TransactionStatus.PENDING,
                    )

            except Exception:
                return Response(
                    {"error": "Erro ao processar saque. Tente novamente."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user.profile).order_by('-created_at')
