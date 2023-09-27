from copy import deepcopy
from datetime import timedelta
from typing import Dict, List, Set

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import linebreaksbr
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from NEMO.decorators import accounting_or_user_office_or_manager_required
from NEMO.forms import AdjustmentRequestForm
from NEMO.mixins import BillableItemMixin
from NEMO.models import (
    AdjustmentRequest,
    AreaAccessRecord,
    Notification,
    RequestMessage,
    RequestStatus,
    Reservation,
    StaffCharge,
    UsageEvent,
    User,
)
from NEMO.typing import QuerySetType
from NEMO.utilities import (
    BasicDisplayTable,
    EmailCategory,
    bootstrap_primary_color,
    export_format_datetime,
    get_full_url,
    quiet_int,
    render_email_template,
    send_mail,
)
from NEMO.views.customization import (EmailsCustomization, UserRequestsCustomization, get_media_file_contents)
from NEMO.views.notifications import (
    create_adjustment_request_notification,
    create_request_message_notification,
    delete_notification,
    get_notifications,
)


@login_required
@require_GET
def adjustment_requests(request):
    if not UserRequestsCustomization.get_bool("adjustment_requests_enabled"):
        return HttpResponseBadRequest("Adjustment requests are not enabled")

    user: User = request.user
    max_requests = quiet_int(UserRequestsCustomization.get("adjustment_requests_display_max"), None)
    adj_requests = AdjustmentRequest.objects.filter(deleted=False)
    if not user.is_facility_manager and not user.is_user_office and not user.is_accounting_officer:
        adj_requests = adj_requests.filter(creator=user)
    if user.is_facility_manager and (user.get_preferences().tool_adjustment_notifications.exists() or user.get_preferences().area_adjustment_notifications.exists()):
        exclude = []
        for adj in adj_requests:
            managers = managers_for_adjustment_request(adj)
            if user not in managers:
                exclude.append(adj.pk)
        adj_requests = adj_requests.exclude(pk__in=exclude)

    dictionary = {
        "pending_adjustment_requests": adj_requests.filter(status=RequestStatus.PENDING),
        "approved_adjustment_requests": adj_requests.filter(status=RequestStatus.APPROVED)[:max_requests],
        "denied_adjustment_requests": adj_requests.filter(status=RequestStatus.DENIED)[:max_requests],
        "adjustment_requests_description": UserRequestsCustomization.get("adjustment_requests_description"),
        "request_notifications": get_notifications(
            request.user, Notification.Types.ADJUSTMENT_REQUEST, delete=not user.is_facility_manager
        ),
        "reply_notifications": get_notifications(request.user, Notification.Types.ADJUSTMENT_REQUEST_REPLY),
    }
    return render(request, "requests/adjustment_requests/adjustment_requests.html", dictionary)


@login_required
@require_http_methods(["GET", "POST"])
def create_adjustment_request(request, request_id=None, item_type_id=None, item_id=None):
    if not UserRequestsCustomization.get_bool("adjustment_requests_enabled"):
        return HttpResponseBadRequest("Adjustment requests are not enabled")

    user: User = request.user

    try:
        adjustment_request = AdjustmentRequest.objects.get(id=request_id)
    except AdjustmentRequest.DoesNotExist:
        adjustment_request = AdjustmentRequest()

    try:
        item_type = ContentType.objects.get_for_id(item_type_id)
        adjustment_request.item = item_type.get_object_for_this_type(pk=item_id)
    # Show times if not missed reservation or if missed reservation but customization is set to show times anyway
    except ContentType.DoesNotExist:
        pass

    change_times_allowed = can_change_times(adjustment_request.item)

    # only change the times if we are provided with a charge and it's allowed
    if item_type_id and adjustment_request.item and change_times_allowed:
        adjustment_request.new_start = adjustment_request.item.start
        adjustment_request.new_end = adjustment_request.item.end

    dictionary = {
        "change_times_allowed": change_times_allowed,
        "eligible_items": user_adjustment_eligible_items(user, adjustment_request.item),
    }

    if request.method == "POST":
        # some extra validation needs to be done here because it depends on the user
        edit = bool(adjustment_request.id)
        errors = []
        if edit:
            if adjustment_request.deleted:
                errors.append("You are not allowed to edit deleted requests.")
            if adjustment_request.status != RequestStatus.PENDING:
                errors.append("Only pending requests can be modified.")
            if adjustment_request.creator != user and not user.is_facility_manager:
                errors.append("You are not allowed to edit a request you didn't create.")

        form = AdjustmentRequestForm(
            request.POST,
            instance=adjustment_request,
            initial={"creator": adjustment_request.creator if edit else user},
        )

        # add errors to the form for better display
        for error in errors:
            form.add_error(None, error)

        if form.is_valid():
            if not edit:
                form.instance.creator = user
            if edit and user.is_facility_manager:
                decision = [state for state in ["approve_request", "deny_request"] if state in request.POST]
                if decision:
                    if next(iter(decision)) == "approve_request":
                        adjustment_request.status = RequestStatus.APPROVED
                    else:
                        adjustment_request.status = RequestStatus.DENIED
                    adjustment_request.reviewer = user

            form.instance.last_updated_by = user
            new_adjustment_request = form.save()

            managers_to_notify: Set[User] = set(list(managers_for_adjustment_request(adjustment_request)))

            create_adjustment_request_notification(new_adjustment_request, managers_to_notify)
            if edit:
                # remove notification for current user and other facility managers
                delete_notification(Notification.Types.ADJUSTMENT_REQUEST, adjustment_request.id, [user])
                if user.is_facility_manager:
                    managers = User.objects.filter(is_active=True, is_facility_manager=True)
                    delete_notification(Notification.Types.ADJUSTMENT_REQUEST, adjustment_request.id, managers)
            send_request_received_email(request, new_adjustment_request, edit, managers_to_notify)
            return redirect("user_requests", "adjustment")
        else:
            item_type = form.cleaned_data.get("item_type")
            item_id = form.cleaned_data.get("item_id")
            if item_type and item_id:
                dictionary["change_times_allowed"] = can_change_times(item_type.get_object_for_this_type(pk=item_id))
            dictionary["form"] = form
            return render(request, "requests/adjustment_requests/adjustment_request.html", dictionary)
    else:
        form = AdjustmentRequestForm(instance=adjustment_request)
        dictionary["form"] = form
        return render(request, "requests/adjustment_requests/adjustment_request.html", dictionary)


@login_required
@require_POST
def adjustment_request_reply(request, request_id):
    if not UserRequestsCustomization.get_bool("adjustment_requests_enabled"):
        return HttpResponseBadRequest("Adjustment requests are not enabled")

    adjustment_request = get_object_or_404(AdjustmentRequest, id=request_id)
    user: User = request.user
    message_content = request.POST["reply_content"]
    expiration = timezone.now() + timedelta(days=30)  # 30 days for adjustment requests replies to expire

    if adjustment_request.status != RequestStatus.PENDING:
        return HttpResponseBadRequest("Replies are only allowed on PENDING requests")
    elif user != adjustment_request.creator and not user.is_facility_manager:
        return HttpResponseBadRequest("Only the creator and managers can reply to adjustment requests")
    elif message_content:
        reply = RequestMessage()
        reply.content_object = adjustment_request
        reply.content = message_content
        reply.author = user
        reply.save()
        create_request_message_notification(reply, Notification.Types.ADJUSTMENT_REQUEST_REPLY, expiration)
        email_interested_parties(
            reply, get_full_url(f"{reverse('user_requests', kwargs={'tab': 'adjustment'})}?#{reply.id}", request)
        )
    return redirect("user_requests", "adjustment")


@login_required
@require_GET
def delete_adjustment_request(request, request_id):
    if not UserRequestsCustomization.get_bool("adjustment_requests_enabled"):
        return HttpResponseBadRequest("Adjustment requests are not enabled")

    adjustment_request = get_object_or_404(AdjustmentRequest, id=request_id)

    if adjustment_request.creator != request.user:
        return HttpResponseBadRequest("You are not allowed to delete a request you didn't create.")
    if adjustment_request and adjustment_request.status != RequestStatus.PENDING:
        return HttpResponseBadRequest("You are not allowed to delete a request that was already completed.")

    adjustment_request.deleted = True
    adjustment_request.save(update_fields=["deleted"])
    delete_notification(Notification.Types.ADJUSTMENT_REQUEST, adjustment_request.id)
    return redirect("user_requests", "adjustment")


def send_request_received_email(request, adjustment_request: AdjustmentRequest, edit, facility_managers: Set[User]):
    user_office_email = EmailsCustomization.get("user_office_email_address")
    adjustment_request_notification_email = get_media_file_contents("adjustment_request_notification_email.html")
    if user_office_email and adjustment_request_notification_email:
        # cc facility managers
        manager_emails = [
            email
            for user in facility_managers
            for email in user.get_emails(user.get_preferences().email_send_adjustment_request_updates)
        ]
        status = (
            "approved"
            if adjustment_request.status == RequestStatus.APPROVED
            else "denied"
            if adjustment_request.status == RequestStatus.DENIED
            else "updated"
            if edit
            else "received"
        )
        absolute_url = get_full_url(reverse("user_requests", kwargs={"tab": "adjustment"}), request)
        color_type = "success" if status == "approved" else "danger" if status == "denied" else "info"
        dictionary = {
            "template_color": bootstrap_primary_color(color_type),
            "adjustment_request": adjustment_request,
            "status": status,
            "adjustment_requests_url": absolute_url,
            "manager_note": adjustment_request.manager_note if status == "denied" else None,
            "user_office": False,
        }
        message = render_email_template(adjustment_request_notification_email, dictionary)
        creator_notification = adjustment_request.creator.get_preferences().email_send_adjustment_request_updates
        if status in ["received", "updated"]:
            send_mail(
                subject=f"Adjustment request {status}",
                content=message,
                from_email=adjustment_request.creator.email,
                to=manager_emails,
                cc=adjustment_request.creator.get_emails(creator_notification),
                email_category=EmailCategory.ADJUSTMENT_REQUESTS,
            )
        else:
            send_mail(
                subject=f"Your adjustment request has been {status}",
                content=message,
                from_email=adjustment_request.reviewer.email,
                to=adjustment_request.creator.get_emails(creator_notification),
                cc=manager_emails,
                email_category=EmailCategory.ADJUSTMENT_REQUESTS,
            )

        # Send separate email to the user office (with the extra note) when a request is approved
        if adjustment_request.status == RequestStatus.APPROVED:
            dictionary["manager_note"] = adjustment_request.manager_note
            dictionary["user_office"] = True
            message = render_email_template(adjustment_request_notification_email, dictionary)
            send_mail(
                subject=f"{adjustment_request.creator.get_name()}'s adjustment request has been {status}",
                content=message,
                from_email=adjustment_request.reviewer.email,
                to=[user_office_email],
                cc=manager_emails,
                email_category=EmailCategory.ADJUSTMENT_REQUESTS,
            )


def email_interested_parties(reply: RequestMessage, reply_url):
    creator: User = reply.content_object.creator
    for user in reply.content_object.creator_and_reply_users():
        if user != reply.author and (user == creator or user.get_preferences().email_new_adjustment_request_reply):
            creator_display = f"{creator.get_name()}'s" if creator != user else "your"
            creator_display_his = creator_display if creator != reply.author else "his"
            subject = f"New reply on {creator_display} adjustment request"
            message = f"""{reply.author.get_name()} also replied to {creator_display_his} adjustment request:
<br><br>
{linebreaksbr(reply.content)}
<br><br>
Please visit {reply_url} to reply"""
            email_notification = user.get_preferences().email_send_adjustment_request_updates
            user.email_user(
                subject=subject,
                message=message,
                from_email=reply.author.email,
                email_notification=email_notification,
                email_category=EmailCategory.ADJUSTMENT_REQUESTS,
            )


def can_change_times(item):
    can_change_reservation_times = UserRequestsCustomization.get_bool("adjustment_requests_missed_reservation_times")
    return item and (not isinstance(item, Reservation) or can_change_reservation_times)


def user_adjustment_eligible_items(user: User, current_item=None) -> List[BillableItemMixin]:
    item_number = UserRequestsCustomization.get_int("adjustment_requests_charges_display_number")
    staff_charges_allowed = UserRequestsCustomization.get_bool("adjustment_requests_staff_staff_charges_enabled")
    date_limit = UserRequestsCustomization.get_date_limit()
    charge_filter: Dict = {"end__gte": date_limit} if date_limit else {}
    return adjustment_eligible_items(staff_charges_allowed, charge_filter, user, current_item, item_number)


def adjustment_eligible_items(staff_charges_allowed: bool, charge_filter=None, user: User=None, current_item=None, item_number=None) -> List[BillableItemMixin]:
    if charge_filter is None:
        charge_filter = {}
    items: List[BillableItemMixin] = []
    if UserRequestsCustomization.get_bool("adjustment_requests_missed_reservation_enabled"):
        missed_filter = deepcopy(charge_filter)
        if user:
            missed_filter["user_id"] = user.id
        items.extend(
            Reservation.objects.filter(missed=True).filter(**missed_filter).order_by("-end")[:item_number]
        )
    if UserRequestsCustomization.get_bool("adjustment_requests_tool_usage_enabled"):
        tool_usage_filter = deepcopy(charge_filter)
        if user:
            tool_usage_filter["user_id"] = user.id
            tool_usage_filter["operator_id"] = user.id
        items.extend(
            UsageEvent.objects.filter(end__isnull=False)
            .filter(**tool_usage_filter)
            .order_by("-end")[:item_number]
        )
    if UserRequestsCustomization.get_bool("adjustment_requests_area_access_enabled"):
        area_access_filter = deepcopy(charge_filter)
        if user:
            area_access_filter["customer_id"] = user.id
        items.extend(
            AreaAccessRecord.objects.filter(end__isnull=False, staff_charge__isnull=True)
            .filter(**area_access_filter)
            .order_by("-end")[:item_number]
        )
    if staff_charges_allowed:
        # Add all remote charges for staff to request for adjustment
        remote_tool_usage_filter = deepcopy(charge_filter)
        remote_area_access_filter = deepcopy(charge_filter)
        remote_staff_time_filter = deepcopy(charge_filter)
        if user:
            remote_tool_usage_filter["operator_id"] = user.id
            remote_area_access_filter["staff_charge__staff_member_id"] = user.id
            remote_staff_time_filter["staff_member_id"] = user.id
        items.extend(
            UsageEvent.objects.filter(remote_work=True, end__isnull=False)
            .filter(**remote_tool_usage_filter)
            .order_by("-end")[:item_number]
        )
        items.extend(
            AreaAccessRecord.objects.filter(end__isnull=False)
            .filter(**remote_area_access_filter)
            .order_by("-end")[:item_number]
        )
        items.extend(StaffCharge.objects.filter(end__isnull=False).filter(**remote_staff_time_filter).order_by("-end")[:item_number])
    if current_item and current_item in items:
        items.remove(current_item)
    # Remove already adjusted charges. filter by id first
    for previously_adjusted in AdjustmentRequest.objects.filter(deleted=False, item_id__in=[item.id for item in items]):
        # Then confirm it's the correct item
        if previously_adjusted.item in items:
            items.remove(previously_adjusted.item)
    items.sort(key=lambda x: (x.get_end(), x.get_start()), reverse=True)
    return items[:item_number]


@accounting_or_user_office_or_manager_required
@require_GET
def csv_export(request):
    return adjustments_csv_export(AdjustmentRequest.objects.filter(deleted=False))


def adjustments_csv_export(request_list: List[AdjustmentRequest]) -> HttpResponse:
    table_result = BasicDisplayTable()
    table_result.add_header(("status", "Status"))
    table_result.add_header(("created_date", "Created date"))
    table_result.add_header(("last_updated", "Last updated"))
    table_result.add_header(("creator", "Creator"))
    table_result.add_header(("item", "Item"))
    table_result.add_header(("new_start", "New start"))
    table_result.add_header(("new_end", "New end"))
    table_result.add_header(("difference", "Difference"))
    table_result.add_header(("reviewer", "Reviewer"))
    for req in request_list:
        req: AdjustmentRequest = req
        table_result.add_row(
            {
                "status": req.get_status_display(),
                "created_date": req.creation_time,
                "last_updated": req.last_updated,
                "creator": req.creator,
                "item": req.item.get_display() if req.item else "",
                "new_start": req.new_start,
                "new_end": req.new_end,
                "difference": req.get_time_difference(),
                "reviewer": req.reviewer,
            }
        )

    filename = f"adjustment_requests_{export_format_datetime()}.csv"
    response = table_result.to_csv()
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def managers_for_adjustment_request(adjustment_request: AdjustmentRequest) -> QuerySetType[User]:
    # Create the list of facility managers to notify/show request to. If the adjustment request has a tool/area and no
    # one added that tool/area to their adjustment request list, send/show to everyone (otherwise nobody would see it)
    tool = getattr(adjustment_request.item, "tool", None) if adjustment_request.item else None
    area = getattr(adjustment_request.item, "area", None) if adjustment_request.item else None
    reviewers = User.objects.filter(is_active=True, is_facility_manager=True)
    if tool:
        reviewers_filter = reviewers.filter(Q(preferences__tool_adjustment_notifications__isnull=True) | Q(
            preferences__tool_adjustment_notifications__in=[tool]))
        if reviewers_filter.exists():
            # Only limit managers if at least one person will receive the notification.
            reviewers = reviewers_filter
    if area:
        reviewers_filter = reviewers.filter(Q(preferences__area_adjustment_notifications__isnull=True) | Q(
            preferences__area_adjustment_notifications__in=[area]))
        if reviewers_filter.exists():
            # Only limit managers if at least one person will receive the notification.
            reviewers = reviewers_filter
    return reviewers
