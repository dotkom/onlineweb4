from redwine.models import Penalty
from rest_framework import serializers
from reversion.models import Revision
from wiki.models.article import ArticleRevision

from apps.approval.models import (
    CommitteeApplication,
    CommitteePriority,
    MembershipApproval,
)
from apps.authentication.models import GroupMember
from apps.authentication.serializers import (
    EmailReadOnlySerializer,
    GroupRoleReadOnlySerializer,
    SpecialPositionSerializer,
)
from apps.events.models import Attendee, CompanyEvent, Extras
from apps.events.serializers import EventSerializer
from apps.feedback.serializers import (
    FeedbackRelationListSerializer,
    GenericSurveySerializer,
)
from apps.inventory.models import Item, ItemCategory
from apps.marks.serializers import (
    MarkUserSerializer,
    RuleAcceptanceSerializer,
    SuspensionSerializer,
)
from apps.online_oidc_provider.serializers import UserConsentReadOnlySerializer
from apps.payment.models import (
    Payment,
    PaymentDelay,
    PaymentPrice,
    PaymentRelation,
    PaymentTransaction,
)
from apps.profiles.serializers import PrivacySerializer
from apps.shop.models import Order as ShopOrder
from apps.shop.models import OrderLine as ShopOrderLine
from apps.webshop.models import Order as WebshopOrder
from apps.webshop.models import OrderLine as WebshopOrderLine
from apps.webshop.models import Product as WebshopProduct
from apps.webshop.models import ProductSize
from apps.webshop.serializers import CategoryReadOnlySerializer

from ...models import OnlineUser
from ...serializers import AllowedUsername, PositionReadOnlySerializer


class AllowedUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedUsername
        fields = ("username", "registered", "note", "expiration_date")


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = ("choice", "note")


class CompaniesSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="company.name")

    class Meta:
        model = CompanyEvent
        fields = ("name",)


class AttendeeSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source="event.event.title")
    event_start = serializers.DateTimeField(source="event.event.event_start")
    event_end = serializers.DateTimeField(source="event.event.event_end")
    location = serializers.CharField(source="event.event.location")
    event_type = serializers.SerializerMethodField()
    extras = ExtrasSerializer()
    companies = CompaniesSerializer(many=True, source="event.event.companies")

    def get_event_type(self, attendee: Attendee):
        return attendee.event.event.get_event_type_display()

    class Meta:
        model = Attendee
        fields = (
            "event_name",
            "event_start",
            "event_end",
            "location",
            "event_type",
            "timestamp",
            "attended",
            "paid",
            "note",
            "show_as_attending_event",
            "extras",
            "companies",
        )


class RevisionSerializer(serializers.ModelSerializer):
    comment = serializers.SerializerMethodField()

    def get_comment(self, revision: Revision):
        return revision.get_comment()

    class Meta:
        model = Revision
        fields = ("date_created", "comment")


class WikiArticleRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRevision
        fields = (
            "user_message",
            "automatic_log",
            "ip_address",
            "modified",
            "created",
            "title",
        )


class GroupMemberSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name_long")
    roles = GroupRoleReadOnlySerializer(many=True)

    class Meta:
        model = GroupMember
        fields = ("group_name", "added", "is_on_leave", "is_retired", "roles")


class PenaltySerializer(serializers.ModelSerializer):
    to = serializers.SerializerMethodField()
    giver = serializers.SerializerMethodField()

    def get_to(self, penalty: Penalty):
        return penalty.to.get_full_name()

    def get_giver(self, penalty: Penalty):
        return penalty.giver.get_full_name()

    class Meta:
        model = Penalty
        fields = (
            "to",
            "giver",
            "amount",
            "committee",
            "reason",
            "date",
            "deleted",
            "item",
            "item_name",
        )


class PaymentTransactionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_items(self, obj: PaymentTransaction):
        return obj.get_items()

    def get_description(self, obj: PaymentTransaction):
        return obj.get_description()

    class Meta:
        model = PaymentTransaction
        fields = ("amount", "used_stripe", "datetime", "status", "description", "items")


class PaymentPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPrice
        fields = ("price", "description")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("description",)


class PaymentRelationSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()
    payment_price = PaymentPriceSerializer()

    class Meta:
        model = PaymentRelation
        fields = ("payment", "payment_price", "datetime", "refunded", "status")


class PaymentDelaySerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()

    class Meta:
        model = PaymentDelay
        fields = ("payment", "valid_to", "active")


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ("size", "description")


class WebshopProductSerializer(serializers.ModelSerializer):
    category = CategoryReadOnlySerializer()

    class Meta:
        model = WebshopProduct
        fields = ("category", "name", "deadline")
        read_only = True


class WebshopOrderSerializer(serializers.ModelSerializer):
    size = ProductSizeSerializer()
    product = WebshopProductSerializer()

    class Meta:
        model = WebshopOrder
        fields = ("product", "price", "quantity", "size")


class WebshopOrderLineSerializer(serializers.ModelSerializer):
    orders = WebshopOrderSerializer(many=True)

    class Meta:
        model = WebshopOrderLine
        fields = ("datetime", "paid", "delivered", "orders", "subtotal")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory

        fields = ("name",)


class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Item
        fields = ("name", "category")


class ShopOrderSerializer(serializers.ModelSerializer):
    content_object = ItemSerializer()

    class Meta:
        model = ShopOrder
        fields = ("price", "quantity", "content_object")


class ShopOrderLineSerializer(serializers.ModelSerializer):
    orders = ShopOrderSerializer(many=True)

    class Meta:
        model = ShopOrderLine
        fields = ("orders", "paid", "datetime")


class MembershipApprovalSerializer(serializers.ModelSerializer):
    applicant = serializers.SerializerMethodField()
    approver = serializers.SerializerMethodField()

    def get_applicant(self, approval: MembershipApproval):
        return approval.applicant.get_full_name()

    def get_approver(self, approval: MembershipApproval):
        return approval.approver.get_full_name() if approval.approver else None

    class Meta:
        model = MembershipApproval
        fields = (
            "applicant",
            "approver",
            "created",
            "processed",
            "processed_date",
            "approved",
            "message",
        )


class CommitteePrioritiySerializer(serializers.ModelSerializer):
    committee = serializers.CharField(source="group.name")

    class Meta:
        model = CommitteePriority
        fields = ("committee", "priority")


class CommitteeApplicationSerializer(serializers.ModelSerializer):
    committee_priorities = CommitteePrioritiySerializer(
        many=True, source="committeepriority_set"
    )

    class Meta:
        model = CommitteeApplication
        fields = (
            "created",
            "modified",
            "applicant",
            "name",
            "application_text",
            "prioritized",
            "committees",
            "committee_priorities",
        )


class UserDataSerializer(serializers.ModelSerializer):
    # Profile
    name = serializers.SerializerMethodField()
    field_of_study = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    privacy = PrivacySerializer()
    member = AllowedUsernameSerializer()
    email_objects = EmailReadOnlySerializer(many=True, source="get_emails")
    # Feedback
    owned_generic_surveys = GenericSurveySerializer(many=True)
    feedbacks = FeedbackRelationListSerializer(many=True)
    # Events
    attendees = AttendeeSerializer(many=True, source="attendee_set")
    created_events = EventSerializer(many=True)
    # Groups
    group_memberships = GroupMemberSerializer(many=True)
    positions = PositionReadOnlySerializer(many=True)
    special_positions = SpecialPositionSerializer(many=True)
    # Redwine
    penalties = PenaltySerializer(many=True)
    given_penalties = PenaltySerializer(many=True, source="penaltygiver")
    # Payments
    payment_delays = PaymentDelaySerializer(many=True, source="paymentdelay_set")
    payment_relations = PaymentRelationSerializer(
        many=True, source="paymentrelation_set"
    )
    payment_transactions = PaymentTransactionSerializer(
        many=True, source="paymenttransaction_set"
    )
    # Purchases
    orderline_set = WebshopOrderLineSerializer(many=True)
    shop_order_lines = ShopOrderLineSerializer(many=True)
    # Marks
    accepted_mark_rule_sets = RuleAcceptanceSerializer(many=True)
    marks = MarkUserSerializer(many=True, source="markuser_set")
    suspensions = SuspensionSerializer(many=True, source="suspension_set")
    # Approval
    applications = MembershipApprovalSerializer(many=True)
    approved_applications = MembershipApprovalSerializer(many=True)
    committeeapplication_set = CommitteeApplicationSerializer(many=True)
    # Wiki
    wiki_article_revisions = WikiArticleRevisionSerializer(
        many=True, source="articlerevision_set"
    )
    # Other
    object_revisions = RevisionSerializer(many=True, source="revision_set")

    # OpenID / Oauth
    user_consents = UserConsentReadOnlySerializer(many=True, source="userconsent_set")

    def get_name(self, user: OnlineUser):
        return user.get_full_name()

    def get_field_of_study(self, user: OnlineUser):
        return user.get_field_of_study_display()

    def get_gender(self, user: OnlineUser):
        return user.get_gender_display()

    class Meta:
        model = OnlineUser
        fields = (
            # User
            "id",
            "is_active",
            "is_committee",
            "is_member",
            "is_staff",
            "last_login",
            "name",
            "username",
            "date_joined",
            # Profile
            "address",
            "allergies",
            "linkedin",
            "rfid",
            "saldo",
            "field_of_study",
            "phone_number",
            "gender",
            "github",
            "rfid",
            "saldo",
            "website",
            "year",
            "zip_code",
            "bio",
            "nickname",
            "compiled",
            "ntnu_username",
            "primary_email",
            "privacy",
            "online_mail",
            "email",
            "email_objects",
            "started_date",
            "image",
            "member",
            # Sync
            "infomail",
            "jobmail",
            # Feedback
            "owned_generic_surveys",
            "feedbacks",
            # Events
            "attendees",
            "created_events",
            # Marks
            "mark_rules_accepted",
            "accepted_mark_rule_sets",
            "marks",
            "suspensions",
            # OpenID / Oauth
            "oauth2_provider_grant",
            "oidc_clients_set",
            "sso_client",
            "user_consents",
            # Wiki
            "nyt_notifications",
            "nyt_settings",
            "revisionpluginrevision_set",
            "attachmentrevision_set",
            "wiki_article_revisions",
            "owned_articles",
            # Groups
            "group_memberships",
            "positions",
            "special_positions",
            # Redwine
            "penalties",
            "given_penalties",
            # Payments
            "payment_delays",
            "payment_relations",
            "payment_transactions",
            # Purchases
            "orderline_set",
            "shop_order_lines",
            # Photoalbum
            "photo_tags",
            "uploaded_photos",
            "created_albums",
            # Approval
            "applications",
            "approved_applications",
            "committeeapplication_set",
            # Posters
            "ordered_posters",
            "assigned_posters",
            # Other
            "magictoken_set",
            "created_articles",
            "object_revisions",
        )
