from django.conf import settings


class VatTypeSale:
    NONE = 'NONE'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    RAW_FISH = 'RAW_FISH'
    LOW = 'LOW'
    EXEMPT_IMPORT_EXPORT = 'EXEMPT_IMPORT_EXPORT'
    EXEMPT = 'EXEMPT'
    OUTSIDE = 'OUTSIDE'
    EXEMPT_REVERSE = 'EXEMPT_REVERSE'

    ALL_CHOICES = (
        (NONE, 'Ingen mva-behandling (inntekter)'),
        (HIGH, 'Utgående merverdiavgift, 25 %'),
        (MEDIUM, 'Utgående merverdiavgift, 15 %'),
        (RAW_FISH, 'Utgående merverdiavgift, 11,11 %'),
        (LOW, 'Utgående merverdiavgift, 12 %'),
        (EXEMPT_IMPORT_EXPORT, 'Utførsel av varer og tjenester, 0 %'),
        (EXEMPT, 'Innenlands omsetning og uttak fritatt for merverdiavgift, 0 %'),
        (OUTSIDE, 'Omsetning utenfor merverdiavgiftsloven'),
        (EXEMPT_REVERSE, 'Ingen mva-behandling (inntekter)'),
    )
    ALL_TYPES = [t for t, d in ALL_CHOICES]


class VatTypePurchase:
    NONE = 'NONE'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    RAW_FISH = 'RAW_FISH'
    LOW = 'LOW'
    EXEMPT_IMPORT_EXPORT = 'EXEMPT_IMPORT_EXPORT'
    HIGH_DIRECT = 'HIGH_DIRECT'
    HIGH_BASIS = 'HIGH_BASIS'
    MEDIUM_DIRECT = 'MEDIUM_DIRECT'
    MEDIUM_BASIS = 'MEDIUM_BASIS'
    NONE_IMPORT_BASIS = 'NONE_IMPORT_BASIS'
    HIGH_IMPORT_DEDUCTIBLE = 'HIGH_IMPORT_DEDUCTIBLE'
    HIGH_IMPORT_NONDEDUCTIBLE = 'HIGH_IMPORT_NONDEDUCTIBLE'
    MEDIUM_IMPORT_DEDUCTIBLE = 'MEDIUM_IMPORT_DEDUCTIBLE'
    MEDIUM_IMPORT_NONDEDUCTIBLE = 'MEDIUM_IMPORT_NONDEDUCTIBLE'
    HIGH_FOREIGN_SERVICE_DEDUCTIBLE = 'HIGH_FOREIGN_SERVICE_DEDUCTIBLE'
    HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE = 'HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE'
    LOW_FOREIGN_SERVICE_DEDUCTIBLE = 'LOW_FOREIGN_SERVICE_DEDUCTIBLE'
    LOW_FOREIGN_SERVICE_NONDEDUCTIBLE = 'LOW_FOREIGN_SERVICE_NONDEDUCTIBLE'
    HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE = 'HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE'
    HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE = 'HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE'

    ALL_CHOICES = (
        (NONE, 'Ingen mva-behandling (anskaffelser)'),
        (HIGH, 'Fradragsberettiget innenlands inngående mva, 25 %'),
        (MEDIUM, 'Fradragsberettiget innenlands inngående mva, 15 %'),
        (RAW_FISH, 'Fradragsberettiget innenlands inngående mva, 11,11 %'),
        (LOW, 'Fradragsberettiget innenlands inngående mva, 12 %'),
        (EXEMPT_IMPORT_EXPORT, 'Innførsel av varer med omvendt avgiftsplikt som er fritatt for innførselsavgift, 0 %'),
        (HIGH_DIRECT, 'Fradragsberettiget innførselsavgift, 25 %'),
        (HIGH_BASIS, 'Faktura ved innførsel av varer, 25 %'),
        (MEDIUM_DIRECT, 'Fradragsberettiget innførselsavgift, 15 %'),
        (MEDIUM_BASIS, 'Faktura ved innførsel av varer, 15 %'),
        (NONE_IMPORT_BASIS, '__UKEJNT__'),
        (HIGH_IMPORT_DEDUCTIBLE, 'Innførsel av varer med omvendt avgiftsplikt med fradragsrett, 25 %'),
        (HIGH_IMPORT_NONDEDUCTIBLE, 'Innførsel av varer med omvendt avgiftsplikt uten fradragsrett, 25 %'),
        (MEDIUM_IMPORT_DEDUCTIBLE, 'Innførsel av varer med omvendt avgiftsplikt med fradragsrett, 15 %'),
        (MEDIUM_IMPORT_NONDEDUCTIBLE, 'Innførsel av varer med omvendt avgiftsplikt uten fradragsrett, 15 %'),
        (HIGH_FOREIGN_SERVICE_DEDUCTIBLE,
         'Tjenester kjøpt fra utlandet med omvendt avgiftsplikt med fradragsrett, 25 %'),
        (HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE,
         'Tjenester kjøpt fra utlandet med omvendt avgiftsplikt uten fradragsrett, 25 %'),
        (LOW_FOREIGN_SERVICE_DEDUCTIBLE,
         'Tjenester kjøpt fra utlandet med omvendt avgiftsplikt med fradragsrett, 12 %'),
        (LOW_FOREIGN_SERVICE_NONDEDUCTIBLE,
         'Tjenester kjøpt fra utlandet med omvendt avgiftsplikt uten fradragsrett, 12 %'),
        (HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE,
         'Innenlands kjøp av varer og tjenester med omvendt avgiftsplikt med fradragsrett, 25 %'),
        (HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE,
         'Innenlands kjøp av varer og tjenester med omvendt avgiftsplikt uten fradragsrett, 25 %'),
    )
    ALL_TYPES = [t for t, d in ALL_CHOICES]


vat_percentage = {
    VatTypeSale.NONE: 0.0,
    VatTypeSale.HIGH: 0.25,
    VatTypeSale.MEDIUM: 0.15,
    VatTypeSale.RAW_FISH: 0.1111,
    VatTypeSale.LOW: 0.12,
    VatTypeSale.EXEMPT_IMPORT_EXPORT: 0.0,
    VatTypeSale.EXEMPT: 0.0,
    VatTypeSale.OUTSIDE: 0.0,
    VatTypeSale.EXEMPT_REVERSE: 0.0,

    VatTypePurchase.NONE: 0.0,
    VatTypePurchase.HIGH: 0.25,
    VatTypePurchase.MEDIUM: 0.15,
    VatTypePurchase.RAW_FISH: 0.1111,
    VatTypePurchase.LOW: 0.12,
    VatTypePurchase.EXEMPT_IMPORT_EXPORT: 0.0,
    VatTypePurchase.HIGH_DIRECT: 0.25,
    VatTypePurchase.HIGH_BASIS: 0.25,
    VatTypePurchase.MEDIUM_DIRECT: 0.15,
    VatTypePurchase.MEDIUM_BASIS: 0.15,
    VatTypePurchase.NONE_IMPORT_BASIS: 0.0,
    VatTypePurchase.HIGH_IMPORT_DEDUCTIBLE: 0.25,
    VatTypePurchase.HIGH_IMPORT_NONDEDUCTIBLE: 0.25,
    VatTypePurchase.MEDIUM_IMPORT_DEDUCTIBLE: 0.15,
    VatTypePurchase.MEDIUM_IMPORT_NONDEDUCTIBLE: 0.15,
    VatTypePurchase.HIGH_FOREIGN_SERVICE_DEDUCTIBLE: 0.25,
    VatTypePurchase.HIGH_FOREIGN_SERVICE_NONDEDUCTIBLE: 0.25,
    VatTypePurchase.LOW_FOREIGN_SERVICE_DEDUCTIBLE: 0.12,
    VatTypePurchase.LOW_FOREIGN_SERVICE_NONDEDUCTIBLE: 0.12,
    VatTypePurchase.HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_DEDUCTIBLE: 0.25,
    VatTypePurchase.HIGH_PURCHASE_OF_EMISSIONSTRADING_OR_GOLD_NONDEDUCTIBLE: 0.25,
}


class FikenStripeAccount:
    # Fiken accounts are configured in "onlineweb4/settings/fiken.py"
    ARRKOM = settings.OW4_FIKEN_ACCOUNT_ARRKOM
    PROKOM = settings.OW4_FIKEN_ACCOUNT_PROKOM
    TRIKOM = settings.OW4_FIKEN_ACCOUNT_TRIKOM
    FAGKOM = settings.OW4_FIKEN_ACCOUNT_FAGKOM

    ALL_ACCOUNTS = (ARRKOM, PROKOM, TRIKOM, FAGKOM,)
    ALL_CHOICES = [(a, a) for a in ALL_ACCOUNTS]


class FikenSaleKind:
    CASH_SALE = 'CASH_SALE'
    INVOICE = 'INVOICE'
    EXTERNAL_INVOICE = 'EXTERNAL_INVOICE'

    ALL_KINDS = (CASH_SALE, INVOICE, EXTERNAL_INVOICE,)
    ALL_CHOICES = [(k, k) for k in ALL_KINDS]
