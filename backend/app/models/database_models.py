from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    password = Column(
        String(255),
        nullable=False,
    )

    role = Column(
        String(50),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    candidate_name = Column(
        String(200),
        nullable=False,
    )

    candidate_email = Column(
        String(200),
        nullable=False,
    )

    role = Column(
        String(200),
        nullable=False,
    )

    status = Column(
        String(50),
        default="active",
    )

    started_at = Column(
        DateTime,
        nullable=True,
    )

    ended_at = Column(
        DateTime,
        nullable=True,
    )

    feature_windows = relationship(
        "FeatureWindow",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

    analyses = relationship(
        "Analysis",
        back_populates="interview",
        cascade="all, delete-orphan",
    )

    report = relationship(
        "Report",
        back_populates="interview",
        uselist=False,
        cascade="all, delete-orphan",
    )


class FeatureWindow(Base):
    __tablename__ = "feature_windows"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        String(100),
        ForeignKey("interviews.interview_id"),
        nullable=False,
        index=True,
    )

    window_number = Column(
        Integer,
        nullable=False,
    )

    feature_data = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    interview = relationship(
        "Interview",
        back_populates="feature_windows",
    )


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        String(100),
        ForeignKey("interviews.interview_id"),
        nullable=False,
        index=True,
    )

    analysis_data = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    interview = relationship(
        "Interview",
        back_populates="analyses",
    )


class Report(Base):
    __tablename__ = "reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        String(100),
        ForeignKey("interviews.interview_id"),
        unique=True,
        nullable=False,
        index=True,
    )

    report_data = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    interview = relationship(
        "Interview",
        back_populates="report",
    )


class InterviewInvitation(Base):
    candidate_link = Column(Text, nullable=True)
    __tablename__ = "interview_invitations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    interview_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    token_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )

    candidate_name = Column(
        String(200),
        nullable=False,
    )

    candidate_email = Column(
        String(200),
        nullable=False,
    )

    role = Column(
        String(200),
        nullable=False,
    )

    created_by = Column(
        Integer,
        nullable=False,
    )

    status = Column(
        String(50),
        default="pending",
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )