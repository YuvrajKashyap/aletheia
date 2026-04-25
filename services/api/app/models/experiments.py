from sqlalchemy import Boolean, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, UpdatedAtMixin


class ExperimentConfig(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "experiment_configs"
    __table_args__ = (
        UniqueConstraint("name"),
        Index("ix_experiment_configs_retrieval_mode", "retrieval_mode"),
        Index("ix_experiment_configs_is_default", "is_default"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    retrieval_mode: Mapped[str] = mapped_column(String, nullable=False)
    bm25_candidate_k: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    dense_candidate_k: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    hybrid_candidate_k: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    rerank_top_n: Mapped[int] = mapped_column(Integer, default=25, nullable=False)
    top_k_final: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    fusion_method: Mapped[str | None] = mapped_column(
        String,
        default="reciprocal_rank_fusion",
        nullable=True,
    )
    fusion_params_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    embedding_model: Mapped[str | None] = mapped_column(String, nullable=True)
    reranker_model: Mapped[str | None] = mapped_column(String, nullable=True)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
