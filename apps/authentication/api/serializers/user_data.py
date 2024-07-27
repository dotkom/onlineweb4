from rest_framework import serializers
from reversion.models import Revision
from wiki.models.article import Article as WikiArticle
from wiki.models.article import ArticleRevision
from wiki.plugins.attachments.models import AttachmentRevision

from apps.approval.models import MembershipApproval
from apps.article.serializers import ArticleSerializer
from apps.authentication.models import GroupMember
from apps.authentication.serializers import (
    GroupRoleReadOnlySerializer,
    SpecialPositionSerializer,
)
from apps.events.models import Attendee, CompanyEvent, Extras
from apps.events.serializers import EventSerializer
from apps.feedback.serializers import (
    FeedbackRelationListSerializer,
    GenericSurveySerializer,
)
from apps.marks.serializers import (
    MarkSerializer,
    RuleAcceptanceSerializer,
    SuspensionSerializer,
)
from apps.payment.models import Payment, PaymentDelay, PaymentPrice, PaymentRelation
from apps.profiles.serializers import PrivacySerializer
from apps.webshop.models import Order as WebshopOrder
from apps.webshop.models import OrderLine as WebshopOrderLine
from apps.webshop.models import Product as WebshopProduct
from apps.webshop.models import ProductSize
from apps.webshop.serializers import CategoryReadOnlySerializer

from ...models import OnlineUser
from ...serializers import Membership, PositionReadOnlySerializer


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ("username", "registered", "note", "expiration_date")


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extras
        fields = ("choice", "note")


class CompaniesSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

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


class WikiAttachmentRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentRevision
        fields = (
            "user_message",
            "automatic_log",
            "ip_address",
            "modified",
            "created",
            "description",
            "file",
        )


class WikiArticleSerializer(serializers.ModelSerializer):
    current_revision = WikiArticleRevisionSerializer()
    group = serializers.CharField(source="group.name_long")

    class Meta:
        model = WikiArticle
        fields = (
            "current_revision",
            "created",
            "modified",
            "group",
            "group_read",
            "group_write",
            "other_read",
            "other_write",
        )


class GroupMemberSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name_long")
    roles = GroupRoleReadOnlySerializer(many=True)

    class Meta:
        model = GroupMember
        fields = ("group_name", "added", "is_on_leave", "is_retired", "roles")


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


class UserDataSerializer(serializers.ModelSerializer):
    # Profile
    name = serializers.SerializerMethodField()
    field_of_study = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    privacy = PrivacySerializer()
    member = MembershipSerializer()
    # Articles
    created_articles = ArticleSerializer(many=True)
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
    # Payments
    payment_delays = PaymentDelaySerializer(many=True, source="paymentdelay_set")
    payment_relations = PaymentRelationSerializer(
        many=True, source="paymentrelation_set"
    )
    # Purchases
    orderline_set = WebshopOrderLineSerializer(many=True)
    # Marks
    accepted_mark_rule_sets = RuleAcceptanceSerializer(many=True)
    marks = MarkSerializer(many=True)
    suspensions = SuspensionSerializer(many=True, source="suspension_set")
    # Approval
    applications = MembershipApprovalSerializer(many=True)
    approved_applications = MembershipApprovalSerializer(many=True)
    # Wiki
    wiki_attachment_revisions = WikiAttachmentRevisionSerializer(
        many=True, source="attachmentrevision_set"
    )
    wiki_article_revisions = WikiArticleRevisionSerializer(
        many=True, source="articlerevision_set"
    )
    owned_articles = WikiArticleSerializer(many=True)
    # Other
    object_revisions = RevisionSerializer(many=True, source="revision_set")

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
            "field_of_study",
            "phone_number",
            "gender",
            "github",
            "website",
            "year",
            "zip_code",
            "bio",
            "nickname",
            "compiled",
            "ntnu_username",
            "email",
            "privacy",
            "online_mail",
            "started_date",
            "image",
            "member",
            # Sync
            "infomail",
            "jobmail",
            # Articles
            "created_articles",
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
            # Wiki
            "wiki_attachment_revisions",
            "wiki_article_revisions",
            "owned_articles",
            # Groups
            "group_memberships",
            "positions",
            "special_positions",
            # Payments
            "payment_delays",
            "payment_relations",
            # Purchases
            "orderline_set",
            # Approval
            "applications",
            "approved_applications",
            # Posters
            "ordered_posters",
            "assigned_posters",
            # Other
            "object_revisions",
        )
