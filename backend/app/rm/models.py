"""
Resource Management module models (P2+P3) — F107–F122, F130.

Covers: Employees (HR), Equipment, Materials/Inventory, Procurement,
Resource Allocation, Financial Planning, Capacity Planning.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import (
    AuditFieldsMixin,
    BasePKMixin,
    NoteMixin,
    OrgMixin,
    PrototypeFlagMixin,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.database import Base

import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class ContractType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"


class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    UNPAID = "unpaid"
    OTHER = "other"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class EquipmentStatus(str, enum.Enum):
    AVAILABLE = "available"
    ALLOCATED = "allocated"
    IN_MAINTENANCE = "in_maintenance"
    OUT_OF_SERVICE = "out_of_service"


class ProcurementStatus(str, enum.Enum):
    DRAFT = "draft"
    REQUESTED = "requested"
    APPROVED = "approved"
    ORDERED = "ordered"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class AllocationStatus(str, enum.Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResourceType(str, enum.Enum):
    EMPLOYEE = "employee"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    EXTERNAL = "external"


class DocumentType_RM(str, enum.Enum):
    INVOICE = "invoice"
    NIR = "nir"
    CONSUMPTION_VOUCHER = "consumption_voucher"
    DELIVERY_NOTE = "delivery_note"


# ─── Employee — F107, F109, F110, F111 ────────────────────────────────────────

class Employee(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Employee record (P2+P3).
    F107: CRUD — name, position, department, contract, cost center.
    F109: Leave/availability calendar.
    F110: Skills & qualifications matrix.
    F111: Salary + configurable hourly rate.
    is_p1=False, is_p2=True, is_p3=True.
    """
    __tablename__ = "employees"

    # Prototype flags — specific P2+P3
    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Link to user (optional — not all employees are system users)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Personal
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Employment — F107
    employee_number: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_center: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False
    )
    contract_type: Mapped[str] = mapped_column(
        Enum(ContractType), default=ContractType.FULL_TIME, nullable=False
    )
    hire_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    termination_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Salary — F111
    gross_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    net_salary: Mapped[float | None] = mapped_column(Float, nullable=True)
    benefits: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    hourly_rate: Mapped[float | None] = mapped_column(Float, nullable=True)  # brut complet / ore normate
    standard_hours_month: Mapped[float] = mapped_column(Float, default=168.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Skills — F110
    skills: Mapped[list | None] = mapped_column(JSON, nullable=True)
    qualifications: Mapped[list | None] = mapped_column(JSON, nullable=True)
    certifications: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Is external/subcontractor — F120
    is_external: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    external_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    external_contract_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_daily_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    leaves = relationship("Leave", back_populates="employee")
    allocations = relationship("ResourceAllocation", back_populates="employee")

    __table_args__ = (
        Index("ix_employee_org_status", "organization_id", "status"),
        Index("ix_employee_department", "organization_id", "department"),
    )


# ─── HR Planning — F108 ──────────────────────────────────────────────────────

class HRPlanningEntry(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    HR planning: open positions, hiring/firing calendar.
    F108: Calendar HR — open positions, target dates.
    """
    __tablename__ = "hr_planning_entries"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    entry_type: Mapped[str] = mapped_column(String(20), nullable=False)  # hire, terminate
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )


# ─── Leave / Availability — F109 ─────────────────────────────────────────────

class Leave(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Employee leave/absence tracking.
    F109: Calendar concedii, verificare disponibilitate la alocare.
    """
    __tablename__ = "leaves"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    leave_type: Mapped[str] = mapped_column(Enum(LeaveType), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    employee = relationship("Employee", back_populates="leaves")

    __table_args__ = (
        Index("ix_leave_employee_dates", "employee_id", "start_date", "end_date"),
    )


# ─── Equipment — F110, F111 (reused for equipment tracking) ──────────────────

class Equipment(Base, BasePKMixin, TimestampMixin, SoftDeleteMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Equipment and machinery tracking (P2+P3).
    Status, allocation, maintenance.
    """
    __tablename__ = "equipment"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        Enum(EquipmentStatus), default=EquipmentStatus.AVAILABLE, nullable=False
    )

    # Details
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    purchase_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    daily_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Maintenance
    next_maintenance_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    maintenance_history: Mapped[list | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_equipment_org_status", "organization_id", "status"),
    )


# ─── Material / Inventory — F112, F113, F114 ─────────────────────────────────

class MaterialStock(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Materials inventory and stock levels.
    F114: Stock levels, minimum alerts, reporting.
    """
    __tablename__ = "material_stocks"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False)

    current_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    minimum_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reserved_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    warehouse: Mapped[str | None] = mapped_column(String(100), nullable=True)

    unit_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Alert flag
    is_below_minimum: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_material_stock_org", "organization_id"),
    )


# ─── Procurement — F112, F113 ────────────────────────────────────────────────

class ProcurementOrder(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin, NoteMixin):
    """
    Purchase orders for materials.
    F112: Planning — supplier, quantity, price, deadline, status.
    F113: Invoices, NIR, consumption vouchers.
    """
    __tablename__ = "procurement_orders"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    order_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    supplier_contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )
    wbs_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wbs_nodes.id"), nullable=True
    )

    status: Mapped[str] = mapped_column(
        Enum(ProcurementStatus), default=ProcurementStatus.DRAFT, nullable=False
    )
    total_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    order_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_delivery: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_delivery: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    line_items = relationship("ProcurementLineItem", back_populates="order", cascade="all, delete-orphan")
    documents = relationship("ProcurementDocument", back_populates="order")

    __table_args__ = (
        Index("ix_procurement_org_status", "organization_id", "status"),
    )


class ProcurementLineItem(Base, BasePKMixin, OrgMixin):
    """Line items in a procurement order."""
    __tablename__ = "procurement_line_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_orders.id"), nullable=False
    )
    material_stock_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("material_stocks.id"), nullable=True
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True
    )

    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    received_quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    order = relationship("ProcurementOrder", back_populates="line_items")


class ProcurementDocument(Base, BasePKMixin, TimestampMixin, OrgMixin):
    """
    Documents associated with procurement (invoices, NIR, consumption vouchers).
    F113: Facturi, NIR-uri, bonuri consum.
    """
    __tablename__ = "procurement_documents"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_orders.id"), nullable=False
    )
    document_type: Mapped[str] = mapped_column(Enum(DocumentType_RM), nullable=False)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    order = relationship("ProcurementOrder", back_populates="documents")


# ─── Resource Allocation — F117, F118, F119, F120, F083 ──────────────────────

class ResourceAllocation(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Resource allocation to projects/phases.
    F117: Employees + materials + budget allocation with conflict semaphore.
    F118: Real-time consumption tracking (allocated vs actual).
    F083: Sync with PM module.
    """
    __tablename__ = "resource_allocations"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    resource_type: Mapped[str] = mapped_column(Enum(ResourceType), nullable=False)

    # Resource reference (one of these will be set)
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )
    equipment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=True
    )

    # Target
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    wbs_node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wbs_nodes.id"), nullable=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True
    )

    # Schedule
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    allocated_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Cost — F119
    planned_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    # Status & conflicts — F117
    status: Mapped[str] = mapped_column(
        Enum(AllocationStatus), default=AllocationStatus.PLANNED, nullable=False
    )
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    conflict_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Allocation percentage (for partial allocations)
    allocation_percent: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)

    employee = relationship("Employee", back_populates="allocations")

    __table_args__ = (
        Index("ix_allocation_project", "project_id"),
        Index("ix_allocation_employee", "employee_id"),
        Index("ix_allocation_dates", "start_date", "end_date"),
    )


# ─── Financial Planning — F115, F116 ─────────────────────────────────────────

class BudgetEntry(Base, BasePKMixin, TimestampMixin, OrgMixin, AuditFieldsMixin):
    """
    Financial planning — budgets per cost center.
    F115: Short & long term planning.
    F116: Cost analysis (actual vs budget).
    """
    __tablename__ = "budget_entries"

    is_p1: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_p2: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_p3: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    cost_center: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    period_month: Mapped[int] = mapped_column(Integer, nullable=False)
    period_year: Mapped[int] = mapped_column(Integer, nullable=False)

    budgeted_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    variance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RON", nullable=False)

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )

    __table_args__ = (
        Index("ix_budget_org_period", "organization_id", "period_year", "period_month"),
        Index("ix_budget_cost_center", "organization_id", "cost_center"),
    )
