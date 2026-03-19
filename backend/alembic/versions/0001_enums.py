"""Create all 46 PostgreSQL enum types.

Revision ID: 0001
Revises:
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all 46 enum types used across 6 modules."""

    # CRM enums
    op.execute("CREATE TYPE contactstage AS ENUM ('PROSPECT', 'POTENTIAL_CLIENT', 'ACTIVE', 'INACTIVE', 'PARTNER')")
    op.execute("CREATE TYPE contacttype AS ENUM ('PF', 'IMM', 'PJ', 'CORPORATION')")
    op.execute("CREATE TYPE interactiontype AS ENUM ('CALL', 'EMAIL', 'MEETING', 'OFFER', 'CONTRACT', 'NOTE', 'VISIT')")
    op.execute("CREATE TYPE propertytype AS ENUM ('BLOC_PANOU', 'BLOC_CARAMIDA', 'CASA_INTERBELICA', 'CASA_POST_1990', 'SPATIU_INDUSTRIAL', 'CLADIRE_COMERCIALA', 'CLADIRE_PUBLICA', 'OTHER')")
    op.execute("CREATE TYPE productcategory AS ENUM ('PRODUCT', 'SERVICE', 'REVENUE', 'EXPENSE')")
    op.execute("CREATE TYPE documentcategory AS ENUM ('CERTIFICATE', 'PHOTO', 'TECHNICAL', 'CONTRACT', 'OFFER', 'INVOICE', 'OTHER')")

    # Pipeline enums
    op.execute("CREATE TYPE opportunitystage AS ENUM ('NEW', 'QUALIFIED', 'SCOPING', 'OFFERING', 'SENT', 'NEGOTIATION', 'WON', 'LOST')")
    op.execute("CREATE TYPE milestonestatus AS ENUM ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')")
    op.execute("CREATE TYPE dependencytype AS ENUM ('FS', 'SS', 'FF', 'SF')")
    op.execute("CREATE TYPE activitytype AS ENUM ('CALL', 'MEETING', 'FOLLOW_UP', 'TECHNICAL_VISIT', 'EMAIL', 'TASK')")
    op.execute("CREATE TYPE activitystatus AS ENUM ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'OVERDUE')")
    op.execute("CREATE TYPE offerstatus AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'SENT', 'NEGOTIATION', 'ACCEPTED', 'REJECTED', 'EXPIRED')")
    op.execute("CREATE TYPE contractstatus AS ENUM ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'SENT', 'SIGNED', 'ACTIVE', 'SUSPENDED', 'TERMINATED', 'COMPLETED')")
    op.execute("CREATE TYPE invoicestatus AS ENUM ('DRAFT', 'ISSUED', 'SENT', 'PAID', 'OVERDUE', 'CANCELLED')")
    op.execute("CREATE TYPE approvalstatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED')")
    op.execute("CREATE TYPE lossreason AS ENUM ('PRICE', 'COMPETITION', 'TIMING', 'NO_BUDGET', 'NO_NEED', 'NO_RESPONSE', 'OTHER')")

    # PM enums
    op.execute("CREATE TYPE projectstatus AS ENUM ('DRAFT', 'KICKOFF', 'PLANNING', 'IN_PROGRESS', 'ON_HOLD', 'POST_EXECUTION', 'CLOSING', 'COMPLETED', 'CANCELLED')")
    op.execute("CREATE TYPE projecttype AS ENUM ('CLIENT', 'INTERNAL')")
    op.execute("CREATE TYPE wbsnodetype AS ENUM ('CHAPTER', 'SUBCHAPTER', 'ARTICLE')")
    op.execute("CREATE TYPE taskstatus AS ENUM ('TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE')")
    op.execute("CREATE TYPE taskdependencytype AS ENUM ('FS', 'SS', 'FF', 'SF')")
    op.execute("CREATE TYPE riskprobability AS ENUM ('VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH')")
    op.execute("CREATE TYPE riskimpact AS ENUM ('NEGLIGIBLE', 'MINOR', 'MODERATE', 'MAJOR', 'CRITICAL')")
    op.execute("CREATE TYPE riskstatus AS ENUM ('IDENTIFIED', 'ASSESSED', 'MITIGATING', 'RESOLVED', 'ACCEPTED')")
    op.execute("CREATE TYPE punchitemstatus AS ENUM ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'VERIFIED')")
    op.execute("CREATE TYPE punchitemseverity AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')")
    op.execute("CREATE TYPE timesheetstatus AS ENUM ('DRAFT', 'SUBMITTED', 'APPROVED', 'REJECTED')")
    op.execute("CREATE TYPE wikiposttype AS ENUM ('POST', 'FILE', 'DOCUMENT')")
    op.execute("CREATE TYPE importsourcetype AS ENUM ('INTERSOFT', 'EDEVIZE', 'CSV', 'EXCEL', 'API')")

    # RM enums
    op.execute("CREATE TYPE employeestatus AS ENUM ('ACTIVE', 'ON_LEAVE', 'SUSPENDED', 'TERMINATED')")
    op.execute("CREATE TYPE contracttype AS ENUM ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'FREELANCE')")
    op.execute("CREATE TYPE leavetype AS ENUM ('ANNUAL', 'SICK', 'PERSONAL', 'MATERNITY', 'UNPAID', 'OTHER')")
    op.execute("CREATE TYPE leavestatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED')")
    op.execute("CREATE TYPE equipmentstatus AS ENUM ('AVAILABLE', 'ALLOCATED', 'IN_MAINTENANCE', 'OUT_OF_SERVICE')")
    op.execute("CREATE TYPE procurementstatus AS ENUM ('DRAFT', 'REQUESTED', 'APPROVED', 'ORDERED', 'PARTIALLY_RECEIVED', 'RECEIVED', 'CANCELLED')")
    op.execute("CREATE TYPE allocationstatus AS ENUM ('PLANNED', 'CONFIRMED', 'ACTIVE', 'COMPLETED', 'CANCELLED')")
    op.execute("CREATE TYPE resourcetype AS ENUM ('EMPLOYEE', 'EQUIPMENT', 'MATERIAL', 'EXTERNAL')")
    op.execute("CREATE TYPE documenttype_rm AS ENUM ('INVOICE', 'NIR', 'CONSUMPTION_VOUCHER', 'DELIVERY_NOTE')")

    # BI enums
    op.execute("CREATE TYPE kpithresholdcolor AS ENUM ('RED', 'YELLOW', 'GREEN')")
    op.execute("CREATE TYPE reportformat AS ENUM ('PDF', 'EXCEL', 'CSV')")
    op.execute("CREATE TYPE dashboardwidgettype AS ENUM ('KPI_CARD', 'CHART', 'TABLE', 'GAUGE', 'FUNNEL', 'MAP', 'CUSTOM')")

    # System enums
    op.execute("CREATE TYPE prototypeenum AS ENUM ('P1', 'P2', 'P3')")
    op.execute("CREATE TYPE roleenum AS ENUM ('ADMIN', 'MANAGER_VANZARI', 'AGENT_COMERCIAL', 'TEHNICIAN')")
    op.execute("CREATE TYPE notificationchannel AS ENUM ('EMAIL', 'IN_APP', 'BOTH')")
    op.execute("CREATE TYPE notificationstatus AS ENUM ('UNREAD', 'READ', 'ARCHIVED')")
    op.execute("CREATE TYPE customfieldtype AS ENUM ('TEXT', 'NUMBER', 'DATE', 'SELECT', 'MULTISELECT', 'BOOLEAN', 'URL', 'EMAIL', 'PHONE')")


def downgrade() -> None:
    """Drop all enum types."""
    op.execute("DROP TYPE IF EXISTS contactstage CASCADE")
    op.execute("DROP TYPE IF EXISTS contacttype CASCADE")
    op.execute("DROP TYPE IF EXISTS interactiontype CASCADE")
    op.execute("DROP TYPE IF EXISTS propertytype CASCADE")
    op.execute("DROP TYPE IF EXISTS productcategory CASCADE")
    op.execute("DROP TYPE IF EXISTS documentcategory CASCADE")
    op.execute("DROP TYPE IF EXISTS opportunitystage CASCADE")
    op.execute("DROP TYPE IF EXISTS milestonestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS dependencytype CASCADE")
    op.execute("DROP TYPE IF EXISTS activitytype CASCADE")
    op.execute("DROP TYPE IF EXISTS activitystatus CASCADE")
    op.execute("DROP TYPE IF EXISTS offerstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS contractstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS invoicestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS approvalstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS lossreason CASCADE")
    op.execute("DROP TYPE IF EXISTS projectstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS projecttype CASCADE")
    op.execute("DROP TYPE IF EXISTS wbsnodetype CASCADE")
    op.execute("DROP TYPE IF EXISTS taskstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS taskdependencytype CASCADE")
    op.execute("DROP TYPE IF EXISTS riskprobability CASCADE")
    op.execute("DROP TYPE IF EXISTS riskimpact CASCADE")
    op.execute("DROP TYPE IF EXISTS riskstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS punchitemstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS punchitemseverity CASCADE")
    op.execute("DROP TYPE IF EXISTS timesheetstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS wikiposttype CASCADE")
    op.execute("DROP TYPE IF EXISTS importsourcetype CASCADE")
    op.execute("DROP TYPE IF EXISTS employeestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS contracttype CASCADE")
    op.execute("DROP TYPE IF EXISTS leavetype CASCADE")
    op.execute("DROP TYPE IF EXISTS leavestatus CASCADE")
    op.execute("DROP TYPE IF EXISTS equipmentstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS procurementstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS allocationstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS resourcetype CASCADE")
    op.execute("DROP TYPE IF EXISTS documenttype_rm CASCADE")
    op.execute("DROP TYPE IF EXISTS kpithresholdcolor CASCADE")
    op.execute("DROP TYPE IF EXISTS reportformat CASCADE")
    op.execute("DROP TYPE IF EXISTS dashboardwidgettype CASCADE")
    op.execute("DROP TYPE IF EXISTS prototypeenum CASCADE")
    op.execute("DROP TYPE IF EXISTS roleenum CASCADE")
    op.execute("DROP TYPE IF EXISTS notificationchannel CASCADE")
    op.execute("DROP TYPE IF EXISTS notificationstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS customfieldtype CASCADE")
