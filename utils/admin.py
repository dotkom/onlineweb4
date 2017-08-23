from django.contrib import admin


class DepositWithdrawalFilter(admin.SimpleListFilter):
    """
    A simple filter to select deposits, withdrawals or empty transactions
    """
    title = 'Transaction type'

    parameter_name = 'amount'

    def lookups(self, request, model_admin):
        """
        Tuples with values for url and display term
        """
        return (
            ('positive', 'Deposit'),
            ('negative', 'Withdrawal'),
            ('empty', 'Empty')
        )

    def queryset(self, request, queryset):
        if self.value() == 'positive':
            return queryset.filter(amount__gt=0)

        if self.value() == 'negative':
            return queryset.filter(amount__lt=0)

        if self.value() == 'empty':
            return queryset.filter(amount=0)
