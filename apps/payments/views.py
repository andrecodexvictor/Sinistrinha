from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from apps.users.models import UserProfile
from .serializers import TransactionSerializer, DepositWithdrawSerializer

class DepositView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user_profile = request.user.profile
            
            # Mock integration logic for deposit
            user_profile.balance += amount
            user_profile.save()
            
            transaction = Transaction.objects.create(
                user=user_profile,
                amount=amount,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                status=Transaction.TransactionStatus.COMPLETED
            )
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WithdrawView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DepositWithdrawSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            user_profile = request.user.profile

            if user_profile.balance < amount:
                return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

            user_profile.balance -= amount
            user_profile.save()

            transaction = Transaction.objects.create(
                user=user_profile,
                amount=amount,
                transaction_type=Transaction.TransactionType.WITHDRAW,
                status=Transaction.TransactionStatus.PENDING # Delay manual validation here
            )
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TransactionHistoryView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user.profile).order_by('-created_at')
